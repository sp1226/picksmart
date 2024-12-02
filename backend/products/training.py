import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from datetime import datetime, timedelta
from .models import *
from .ml_models import ProductRecommender
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle
from torch.serialization import add_safe_globals

# 필요한 모든 타입을 안전한 글로벌로 등록
add_safe_globals([
    MinMaxScaler,
    dict,
    np.ndarray,
    torch.nn.Parameter,
    torch._utils._rebuild_tensor_v2
])

class RecommendationDataset(Dataset):
    def __init__(self):
        self.users = list(User.objects.all())
        self.products = list(Product.objects.all())
        self.user_to_idx = {user.id: idx for idx, user in enumerate(self.users)}
        self.product_to_idx = {product.id: idx for idx, product in enumerate(self.products)}
        self.interactions = UserBehavior.objects.all()
        self.scaler = MinMaxScaler()
        self.prepare_data()
            
    def prepare_data(self):
        self.training_data = []
        all_behavior_data = []

        # 첫 번째 패스: 행동 데이터 수집 및 스케일러 피팅
        print("행동 데이터 수집 중...")
        for interaction in self.interactions:
            try:
                behavior_data = [
                    interaction.click_count,
                    interaction.view_duration,
                    interaction.cart_add_count
                ]
                all_behavior_data.append(behavior_data)
            except Exception as e:
                print(f"행동 데이터 수집 중 오류 발생: {e}")
                continue

        # 스케일러 피팅
        if all_behavior_data:
            print(f"총 {len(all_behavior_data)}개의 행동 데이터로 스케일러 피팅")
            self.scaler.fit(all_behavior_data)
        else:
            print("행동 데이터가 없습니다.")
            return

        # 두 번째 패스: 훈련 데이터 생성
        print("훈련 데이터 생성 중...")
        for interaction in self.interactions:
            try:
                user_profile = interaction.user.userprofile

                # 사용자 특성 원-핫 인코딩
                gender_enc = [0, 0, 0]
                gender_enc[['M', 'F', 'O'].index(user_profile.gender)] = 1

                age_enc = [0, 0, 0, 0, 0]
                age_enc[['10', '20', '30', '40', '50'].index(user_profile.age_group)] = 1

                income_enc = [0, 0, 0]
                income_enc[['L', 'M', 'H'].index(user_profile.income_level)] = 1

                # 행동 데이터 정규화
                behavior_data = np.array([
                    interaction.click_count,
                    interaction.view_duration,
                    interaction.cart_add_count
                ]).reshape(1, -1)
                behavior_data = self.scaler.transform(behavior_data)[0]

                # 목표값 (구매 여부)
                target = 1.0 if interaction.purchase_count > 0 else 0.0

                user_idx = self.user_to_idx[interaction.user.id]
                product_idx = self.product_to_idx[interaction.product.id]

                self.training_data.append({
                    'user_id': user_idx,
                    'product_id': product_idx,
                    'user_features': gender_enc + age_enc + income_enc,
                    'behavior_data': behavior_data.tolist(),
                    'target': target
                })
            except Exception as e:
                print(f"훈련 데이터 생성 중 오류 발생: {e}")
                continue

        print(f"총 {len(self.training_data)}개의 훈련 데이터 생성 완료")

    def __len__(self):
        return len(self.training_data)
    
    def __getitem__(self, idx):
        item = self.training_data[idx]
        return (
            torch.tensor(item['user_id']),
            torch.tensor(item['product_id']),
            torch.tensor(item['user_features'], dtype=torch.float),
            torch.tensor(item['behavior_data'], dtype=torch.float),
            torch.tensor(item['target'], dtype=torch.float)
        )
        
def save_model(model, user_to_idx, product_to_idx, scaler, path='model_weights'):
    """모델과 메타데이터를 안전하게 저장"""
    try:
        # weights_only 파라미터 제거
        torch.save({
            'model_state_dict': model.state_dict(),
        }, f'{path}.pth')
        
        # 메타데이터 별도 저장
        metadata = {
            'user_to_idx': user_to_idx,
            'product_to_idx': product_to_idx,
            'scaler_params': {
                'min_': scaler.min_,
                'scale_': scaler.scale_,
                'data_min_': getattr(scaler, 'data_min_', None),
                'data_max_': getattr(scaler, 'data_max_', None),
                'data_range_': getattr(scaler, 'data_range_', None)
            }
        }
        torch.save(metadata, f'{path}_metadata.pth')
        print("모델이 안전하게 저장되었습니다.")
        return True
    except Exception as e:
        print(f"모델 저장 중 오류 발생: {e}")
        return False   

def train_model(epochs=10, batch_size=32, learning_rate=0.001):
    try:
        print("데이터셋 초기화 중...")
        dataset = RecommendationDataset()
        
        if len(dataset) == 0:
            raise ValueError("훈련 데이터가 없습니다!")
        
        print(f"총 {len(dataset)}개의 훈련 데이터로 학습을 시작합니다.")
        
        # 데이터로더 설정
        dataloader = DataLoader(
            dataset, 
            batch_size=min(batch_size, len(dataset)), 
            shuffle=True
        )
        
        # 모델 초기화
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"디바이스: {device}")
        
        model = ProductRecommender(
            n_users=len(dataset.users),
            n_products=len(dataset.products)
        )
        model.to(device)
        
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        criterion = torch.nn.BCELoss()
        
        # 훈련 루프
        print("모델 훈련 시작...")
        best_loss = float('inf')
        for epoch in range(epochs):
            model.train()
            total_loss = 0
            for batch in dataloader:
                # 배치 데이터를 GPU로 이동
                user_ids, product_ids, user_features, behavior_data, targets = [
                    x.to(device) for x in batch
                ]
                
                optimizer.zero_grad()
                predictions = model(user_ids, product_ids, user_features, behavior_data)
                loss = criterion(predictions.squeeze(), targets)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(dataloader)
            print(f'Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}')

            # 베스트 모델 저장
            if avg_loss < best_loss:
                best_loss = avg_loss
                print(f"새로운 best loss ({best_loss:.4f}) 달성, 모델 저장 중...")
                
                # 안전한 방식으로 모델 저장
                save_success = save_model(
                    model=model,
                    user_to_idx=dataset.user_to_idx,
                    product_to_idx=dataset.product_to_idx,
                    scaler=dataset.scaler,
                    path='model_weights'
                )
                
                if save_success:
                    print("모델이 안전하게 저장되었습니다.")
                else:
                    print("모델 저장 중 오류가 발생했습니다.")

        
        print(f"훈련 완료! 최종 Loss: {best_loss:.4f}")
        return True

    except Exception as e:
        print(f"모델 훈련 중 에러 발생: {str(e)}")
        return False