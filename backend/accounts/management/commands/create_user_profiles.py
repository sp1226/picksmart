# backend/accounts/management/commands/create_user_profiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from products.models import ProductCategory

class Command(BaseCommand):
    help = '기존 사용자들을 위한 프로필 생성'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0
        
        # 카테고리 딕셔너리 생성
        categories = {
            'male': {
                'L': ['전자기기', '도서'],
                'M': ['전자기기', '스포츠/레저'],
                'H': ['전자기기', '스포츠/레저', '패션잡화']
            },
            'female': {
                'L': ['화장품', '문구/취미'],
                'M': ['패션잡화', '화장품'],
                'H': ['패션잡화', '화장품', '전자기기']
            }
        }
        
        for user in users:
            try:
                if not hasattr(user, 'userprofile'):
                    # 사용자명에서 정보 추출 (예: male_20_low)
                    parts = user.username.split('_')
                    if len(parts) == 3:
                        gender = 'M' if parts[0] == 'male' else 'F'
                        age_group = parts[1]
                        income_level = 'L' if parts[2] == 'low' else ('H' if parts[2] == 'high' else 'M')
                        
                        # 프로필 생성
                        profile = UserProfile.objects.create(
                            user=user,
                            gender=gender,
                            age_group=age_group,
                            income_level=income_level
                        )
                        
                        # 선호 카테고리 설정
                        gender_key = 'male' if gender == 'M' else 'female'
                        preferred_category_names = categories[gender_key][income_level]
                        preferred_categories = ProductCategory.objects.filter(
                            name__in=preferred_category_names
                        )
                        profile.preferred_categories.add(*preferred_categories)
                        
                        # 실제 행동 데이터 기반으로 선호도 업데이트
                        profile.update_preferred_categories()
                        
                        created_count += 1
                        self.stdout.write(f'Created profile for {user.username}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating profile for {user.username}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count}개의 프로필이 생성되었습니다.'))
