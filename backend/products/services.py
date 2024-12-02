# backend/products/services.py

import os
import torch
from torch.serialization import add_safe_globals
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from django.db.models import Sum, Avg
from .ml_models import ProductRecommender
from .models import Product, UserBehavior, ProductView, RecommendationLog, ProductFavorite
from accounts.models import UserProfile
from django.contrib.auth.models import User

# 안전한 타입들 등록
add_safe_globals([
    MinMaxScaler,
    dict,
    np.ndarray,
    torch.nn.Parameter,
    torch._utils._rebuild_tensor_v2
])

class RecommendationService:
    def __init__(self, user):
        self.user = user
        self.model = None
        self.user_to_idx = {}
        self.product_to_idx = {}
        self.scaler = None
        self._load_model()
        
    def _load_model(self):
        """모델과 관련 데이터 로드"""
        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model_path = 'model_weights.pth'
            
            # 스케일러 초기화 및 기본 fit
            self.scaler = MinMaxScaler()
            default_behavior_data = np.array([
                [0, 0, 0],      # 최소값
                [100, 3600, 100]  # 최대 예상값
            ])
            self.scaler.fit(default_behavior_data)
            
            # 모델 초기화
            self.model = ProductRecommender(
                n_users=User.objects.count(),
                n_products=Product.objects.count()
            )
            self.model.to(device)
            self.model.eval()

            # 기본값 설정
            self.user_to_idx = {}
            self.product_to_idx = {}

            if os.path.exists(model_path):
                try:
                    # 모델 가중치 로드
                    checkpoint = torch.load(
                        model_path,
                        map_location=device,
                        weights_only=True
                    )
                    self.model.load_state_dict(checkpoint['model_state_dict'])

                    # 메타데이터 로드
                    if os.path.exists('model_metadata.pth'):
                        metadata = torch.load('model_metadata.pth', map_location=device)
                        self.user_to_idx = metadata.get('user_to_idx', {})
                        self.product_to_idx = metadata.get('product_to_idx', {})
                        
                        # MinMaxScaler 상태 업데이트
                        if 'scaler_params' in metadata:
                            scaler_state = metadata['scaler_params']
                            self.scaler.min_ = scaler_state['min_']
                            self.scaler.scale_ = scaler_state['scale_']
                            self.scaler.data_min_ = scaler_state.get('data_min_')
                            self.scaler.data_max_ = scaler_state.get('data_max_')
                            self.scaler.data_range_ = scaler_state.get('data_range_')
                            
                except Exception as e:
                    print(f"Error during model loading: {e}")
            else:
                print("Model weights file not found, using defaults")
                
        except Exception as e:
            print(f"Error in model loading: {e}")

    def predict_user_interest(self, product_id):
        """특정 상품에 대한 사용자의 관심도 예측"""
        try:
            # 필요한 인덱스 가져오기
            device = next(self.model.parameters()).device
            user_idx = self.user_to_idx.get(self.user.id, 0)
            product_idx = self.product_to_idx.get(product_id, 0)

            # 사용자 프로필 데이터 준비
            user_profile = self.user.userprofile
            
            # 성별 원-핫 인코딩
            gender_enc = [0, 0, 0]  # [M, F, O]
            gender_map = {'M': 0, 'F': 1, 'O': 2}
            gender_enc[gender_map.get(user_profile.gender, 2)] = 1

            # 연령대 원-핫 인코딩
            age_enc = [0, 0, 0, 0, 0]  # [10, 20, 30, 40, 50]
            age_map = {'10': 0, '20': 1, '30': 2, '40': 3, '50': 4}
            age_enc[age_map.get(user_profile.age_group, 1)] = 1

            # 소득수준 원-핫 인코딩
            income_enc = [0, 0, 0]  # [L, M, H]
            income_map = {'L': 0, 'M': 1, 'H': 2}
            income_enc[income_map.get(user_profile.income_level, 1)] = 1

            # 행동 데이터 가져오기
            behavior = UserBehavior.objects.filter(
                user=self.user,
                product_id=product_id
            ).first()

            behavior_data = np.array([[
                behavior.click_count if behavior else 0,
                behavior.view_duration if behavior else 0,
                behavior.cart_add_count if behavior else 0
            ]], dtype=np.float32)  # 2D array로 직접 생성
            
            # 스케일러 적용
            behavior_data = self.scaler.transform(behavior_data)
            behavior_tensor = torch.from_numpy(behavior_data).float().to(device)

            # 텐서 준비
            user_id = torch.tensor([user_idx]).to(device)
            product_id = torch.tensor([product_idx]).to(device)
            user_features = torch.tensor([gender_enc + age_enc + income_enc]).float().to(device)

            # 예측
            with torch.no_grad():
                prediction = self.model(
                    user_id,
                    product_id,
                    user_features,
                    behavior_tensor
                )
                
            return prediction.item()

        except Exception as e:
            print(f"Error in predict_user_interest: {str(e)}")
            return 0.0

    def get_recommendations(self, limit=8):
        """사용자 맞춤 상품 추천"""
        try:
            # 모든 상품 가져오기
            all_products = Product.objects.all()
            predictions = []

            # 각 상품에 대한 사용자 관심도 예측
            for product in all_products:
                try:
                    score = self.predict_user_interest(product.id)
                    predictions.append((product, score))
                except Exception as e:
                    print(f"Error predicting interest for product {product.id}: {str(e)}")
                    continue

            # 점수 기준 내림차순 정렬
            predictions.sort(key=lambda x: x[1], reverse=True)
            
            # 상위 N개 상품 반환
            recommended_products = [pred[0] for pred in predictions[:limit]]
            return recommended_products

        except Exception as e:
            print(f"Error in get_recommendations: {str(e)}")
            # 에러 발생시 조회수 기준으로 상품 반환
            return Product.objects.all().order_by('-total_views')[:limit]

def save_model(model, user_to_idx, product_to_idx, scaler, path='model_weights'):
    """모델과 메타데이터를 안전하게 저장"""
    try:
        # 모델 가중치 저장
        torch.save({
            'model_state_dict': model.state_dict(),
        }, f'{path}.pth')
        
        # 메타데이터와 scaler 상태 저장
        metadata = {
            'user_to_idx': user_to_idx,
            'product_to_idx': product_to_idx,
            'scaler_params': {
                'min_': scaler.min_,
                'scale_': scaler.scale_,
                'data_min_': scaler.data_min_,
                'data_max_': scaler.data_max_,
                'data_range_': scaler.data_range_,
                'feature_range': scaler.feature_range,
                'clip': scaler.clip
            }
        }
        torch.save(metadata, f'{path}_metadata.pth')
        print("모델이 안전하게 저장되었습니다.")
        return True
    except Exception as e:
        print(f"모델 저장 중 오류 발생: {e}")
        return False