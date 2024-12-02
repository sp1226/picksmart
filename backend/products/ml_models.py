# backend/products/ml_models.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class ProductRecommender(nn.Module):
    def __init__(self, n_users, n_products, embedding_dim=50):
        super().__init__()
        
        # 임베딩 레이어
        self.user_embedding = nn.Embedding(n_users, embedding_dim)
        self.product_embedding = nn.Embedding(n_products, embedding_dim)
        
        # 사용자 특성 처리를 위한 레이어
        self.user_features = nn.Sequential(
            nn.Linear(11, 32),  # 성별(3) + 연령대(5) + 소득수준(3) = 11
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # 행동 데이터 처리를 위한 레이어
        self.behavior_features = nn.Sequential(
            nn.Linear(3, 32),  # 클릭수 + 체류시간 + 장바구니추가수
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # 최종 예측 레이어
        self.predictor = nn.Sequential(
            nn.Linear(embedding_dim + 64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, user_ids, product_ids, user_features, behavior_data):
        # 임베딩
        user_embeds = self.user_embedding(user_ids)
        product_embeds = self.product_embedding(product_ids)
        
        # 특성 처리
        user_feat = self.user_features(user_features)
        behavior_feat = self.behavior_features(behavior_data)
        
        # 모든 특성 결합
        combined = torch.cat([
            user_embeds * product_embeds,
            user_feat,
            behavior_feat
        ], dim=1)
        
        # 최종 예측
        return self.predictor(combined)
