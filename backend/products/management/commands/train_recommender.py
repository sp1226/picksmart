# backend/products/management/commands/train_recommender.py
from django.core.management.base import BaseCommand
from products.training import train_model
from django.contrib.auth.models import User
from accounts.models import UserProfile  # UserProfile을 accounts에서 import


class Command(BaseCommand):
    help = '추천 시스템 모델 재훈련'

    def add_arguments(self, parser):
        parser.add_argument(
            '--epochs',
            type=int,
            default=10,
            help='훈련 에포크 수'
        )

    def handle(self, *args, **kwargs):
        epochs = kwargs['epochs']
        self.stdout.write('추천 시스템 모델 훈련 시작...')
        
        try:
            train_model(epochs=epochs)
            self.stdout.write(self.style.SUCCESS('모델 훈련 완료!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'훈련 중 에러 발생: {str(e)}'))