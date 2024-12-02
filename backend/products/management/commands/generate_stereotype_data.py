# backend/products/management/commands/generate_stereotype_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Product, ProductCategory, UserBehavior
from accounts.models import UserProfile  # UserProfile을 accounts에서 import
import random


class Command(BaseCommand):
    help = '사용자 그룹별 스테레오타입 데이터 생성'

    def handle(self, *args, **kwargs):
        # 카테고리 및 상품 정의
        categories_data = [
            {
                'name': '전자기기',
                'products': [
                    {'name': '기계식키보드', 'price': 158000, 'description': 'RGB 백라이트 탑재 게이밍 키보드'},
                    {'name': '게이밍마우스', 'price': 89000, 'description': '고성능 센서 탑재 게이밍 마우스'},
                    {'name': '노이즈캔슬링헤드폰', 'price': 290000, 'description': '프리미엄 무선 헤드폰'},
                    {'name': '게이밍노트북', 'price': 1890000, 'description': '고성능 게이밍 노트북'},
                    {'name': '태블릿PC', 'price': 890000, 'description': '대화면 태블릿'},
                    {'name': '스마트워치', 'price': 350000, 'description': '건강관리 스마트워치'}
                ]
            },
            {
                'name': '패션잡화',
                'products': [
                    {'name': '명품가방', 'price': 2890000, 'description': '프리미엄 브랜드 가방'},
                    {'name': '명품지갑', 'price': 890000, 'description': '프리미엄 브랜드 지갑'},
                    {'name': '명품벨트', 'price': 590000, 'description': '프리미엄 브랜드 벨트'},
                    {'name': '명품선글라스', 'price': 490000, 'description': '프리미엄 브랜드 선글라스'},
                    {'name': '캐주얼백팩', 'price': 89000, 'description': '실용적인 백팩'},
                    {'name': '크로스백', 'price': 159000, 'description': '데일리 크로스백'}
                ]
            },
            {
                'name': '화장품',
                'products': [
                    {'name': '고급스킨케어세트', 'price': 450000, 'description': '프리미엄 스킨케어 세트'},
                    {'name': '프리미엄립스틱', 'price': 68000, 'description': '고발색 럭셔리 립스틱'},
                    {'name': '명품향수', 'price': 250000, 'description': '고급 브랜드 향수'},
                    {'name': '프리미엄파운데이션', 'price': 89000, 'description': '완벽 커버 파운데이션'},
                    {'name': '기초화장품세트', 'price': 178000, 'description': '기초 스킨케어 세트'},
                    {'name': '메이크업팔레트', 'price': 98000, 'description': '올인원 메이크업 팔레트'}
                ]
            },
            {
                'name': '도서',
                'products': [
                    {'name': 'IT전문서적', 'price': 45000, 'description': '최신 IT 기술서'},
                    {'name': '자기계발서', 'price': 28000, 'description': '베스트셀러 자기계발서'},
                    {'name': '소설책', 'price': 25000, 'description': '인기 소설'},
                    {'name': '만화책', 'price': 15000, 'description': '인기 만화시리즈'},
                    {'name': '과학도서', 'price': 35000, 'description': '과학 교양서'},
                    {'name': '수험서', 'price': 38000, 'description': '자격증 수험서'}
                ]
            },
            {
                'name': '스포츠/레저',
                'products': [
                    {'name': '요가매트', 'price': 89000, 'description': '프리미엄 요가매트'},
                    {'name': '테니스라켓', 'price': 150000, 'description': '전문가용 테니스라켓'},
                    {'name': '골프클럽세트', 'price': 1290000, 'description': '프리미엄 골프클럽 세트'},
                    {'name': '러닝화', 'price': 159000, 'description': '고급 러닝화'},
                    {'name': '헬스용품세트', 'price': 250000, 'description': '홈트레이닝 세트'},
                    {'name': '등산용품', 'price': 280000, 'description': '등산 장비 세트'}
                ]
            },
            {
                'name': '문구/취미',
                'products': [
                    {'name': '프리미엄만년필', 'price': 280000, 'description': '고급 만년필'},
                    {'name': '미술용품세트', 'price': 150000, 'description': '전문가용 미술도구 세트'},
                    {'name': '다이어리', 'price': 35000, 'description': '프리미엄 다이어리'},
                    {'name': '필기구세트', 'price': 45000, 'description': '고급 필기구 세트'},
                    {'name': '스케치북', 'price': 25000, 'description': '전문가용 스케치북'},
                    {'name': '취미키트', 'price': 89000, 'description': 'DIY 취미 키트'}
                ]
            }
        ]

# 사용자 그룹별 선호도 정의
        user_preferences = {
            # 10대 그룹
            ('M', '10', 'L'): {  # 10대 남성 저소득
                '전자기기': 0.9,  # 게임, IT 기기에 매우 높은 관심
                '패션잡화': 0.3,
                '화장품': 0.1,
                '도서': 0.5,     # 만화, 게임 관련 서적
                '스포츠/레저': 0.4,
                '문구/취미': 0.6  # 학업 관련 문구
            },
            ('M', '10', 'M'): {  # 10대 남성 중소득
                '전자기기': 0.9,
                '패션잡화': 0.4,
                '화장품': 0.2,
                '도서': 0.6,
                '스포츠/레저': 0.5,
                '문구/취미': 0.6
            },
            ('M', '10', 'H'): {  # 10대 남성 고소득
                '전자기기': 1.0,
                '패션잡화': 0.5,
                '화장품': 0.2,
                '도서': 0.6,
                '스포츠/레저': 0.6,
                '문구/취미': 0.7
            },
            ('F', '10', 'L'): {  # 10대 여성 저소득
                '전자기기': 0.4,
                '패션잡화': 0.7,
                '화장품': 0.8,
                '도서': 0.6,
                '스포츠/레저': 0.3,
                '문구/취미': 0.8
            },
            ('F', '10', 'M'): {  # 10대 여성 중소득
                '전자기기': 0.5,
                '패션잡화': 0.8,
                '화장품': 0.9,
                '도서': 0.6,
                '스포츠/레저': 0.4,
                '문구/취미': 0.8
            },
            ('F', '10', 'H'): {  # 10대 여성 고소득
                '전자기기': 0.6,
                '패션잡화': 0.9,
                '화장품': 1.0,
                '도서': 0.6,
                '스포츠/레저': 0.5,
                '문구/취미': 0.9
            },

            # 20대 그룹
            ('M', '20', 'L'): {  # 20대 남성 저소득
                '전자기기': 0.8,
                '패션잡화': 0.4,
                '화장품': 0.2,
                '도서': 0.6,
                '스포츠/레저': 0.5,
                '문구/취미': 0.3
            },
            ('M', '20', 'M'): {
                '전자기기': 0.9,
                '패션잡화': 0.6,
                '화장품': 0.3,
                '도서': 0.6,
                '스포츠/레저': 0.6,
                '문구/취미': 0.4
            },
            ('M', '20', 'H'): {
                '전자기기': 1.0,
                '패션잡화': 0.8,
                '화장품': 0.4,
                '도서': 0.7,
                '스포츠/레저': 0.8,
                '문구/취미': 0.5
            },
            ('F', '20', 'L'): {
                '전자기기': 0.5,
                '패션잡화': 0.7,
                '화장품': 0.8,
                '도서': 0.6,
                '스포츠/레저': 0.4,
                '문구/취미': 0.5
            },
            ('F', '20', 'M'): {
                '전자기기': 0.6,
                '패션잡화': 0.8,
                '화장품': 0.9,
                '도서': 0.7,
                '스포츠/레저': 0.5,
                '문구/취미': 0.6
            },
            ('F', '20', 'H'): {
                '전자기기': 0.7,
                '패션잡화': 1.0,
                '화장품': 1.0,
                '도서': 0.7,
                '스포츠/레저': 0.6,
                '문구/취미': 0.7
            },

# 30대 그룹
            ('M', '30', 'L'): {
                '전자기기': 0.7,
                '패션잡화': 0.5,
                '화장품': 0.3,
                '도서': 0.6,
                '스포츠/레저': 0.6,
                '문구/취미': 0.3
            },
            ('M', '30', 'M'): {
                '전자기기': 0.8,
                '패션잡화': 0.7,
                '화장품': 0.4,
                '도서': 0.7,
                '스포츠/레저': 0.8,
                '문구/취미': 0.4
            },
            ('M', '30', 'H'): {
                '전자기기': 0.9,
                '패션잡화': 0.9,
                '화장품': 0.5,
                '도서': 0.8,
                '스포츠/레저': 0.9,
                '문구/취미': 0.5
            },
            ('F', '30', 'L'): {
                '전자기기': 0.4,
                '패션잡화': 0.7,
                '화장품': 0.8,
                '도서': 0.6,
                '스포츠/레저': 0.5,
                '문구/취미': 0.4
            },
            ('F', '30', 'M'): {
                '전자기기': 0.5,
                '패션잡화': 0.8,
                '화장품': 0.9,
                '도서': 0.7,
                '스포츠/레저': 0.7,
                '문구/취미': 0.5
            },
            ('F', '30', 'H'): {
                '전자기기': 0.6,
                '패션잡화': 1.0,
                '화장품': 1.0,
                '도서': 0.8,
                '스포츠/레저': 0.8,
                '문구/취미': 0.6
            },

            # 40대 그룹
            ('M', '40', 'L'): {
                '전자기기': 0.5,
                '패션잡화': 0.4,
                '화장품': 0.2,
                '도서': 0.6,
                '스포츠/레저': 0.7,
                '문구/취미': 0.3
            },
            ('M', '40', 'M'): {
                '전자기기': 0.6,
                '패션잡화': 0.6,
                '화장품': 0.3,
                '도서': 0.7,
                '스포츠/레저': 0.9,
                '문구/취미': 0.4
            },
            ('M', '40', 'H'): {
                '전자기기': 0.7,
                '패션잡화': 0.8,
                '화장품': 0.4,
                '도서': 0.8,
                '스포츠/레저': 1.0,
                '문구/취미': 0.5
            },
            ('F', '40', 'L'): {
                '전자기기': 0.3,
                '패션잡화': 0.6,
                '화장품': 0.7,
                '도서': 0.6,
                '스포츠/레저': 0.6,
                '문구/취미': 0.4
            },
            ('F', '40', 'M'): {
                '전자기기': 0.4,
                '패션잡화': 0.8,
                '화장품': 0.8,
                '도서': 0.7,
                '스포츠/레저': 0.8,
                '문구/취미': 0.5
            },
            ('F', '40', 'H'): {
                '전자기기': 0.5,
                '패션잡화': 0.9,
                '화장품': 0.9,
                '도서': 0.8,
                '스포츠/레저': 0.9,
                '문구/취미': 0.6
            },

            # 50대 이상 그룹
            ('M', '50', 'L'): {
                '전자기기': 0.3,
                '패션잡화': 0.3,
                '화장품': 0.1,
                '도서': 0.7,
                '스포츠/레저': 0.8,
                '문구/취미': 0.4
            },
            ('M', '50', 'M'): {
                '전자기기': 0.4,
                '패션잡화': 0.5,
                '화장품': 0.2,
                '도서': 0.8,
                '스포츠/레저': 0.9,
                '문구/취미': 0.5
            },
            ('M', '50', 'H'): {
                '전자기기': 0.5,
                '패션잡화': 0.7,
                '화장품': 0.3,
                '도서': 0.9,
                '스포츠/레저': 1.0,
                '문구/취미': 0.6
            },
            ('F', '50', 'L'): {
                '전자기기': 0.2,
                '패션잡화': 0.5,
                '화장품': 0.6,
                '도서': 0.7,
                '스포츠/레저': 0.7,
                '문구/취미': 0.5
            },
            ('F', '50', 'M'): {
                '전자기기': 0.3,
                '패션잡화': 0.7,
                '화장품': 0.7,
                '도서': 0.8,
                '스포츠/레저': 0.8,
                '문구/취미': 0.6
            },
            ('F', '50', 'H'): {
                '전자기기': 0.4,
                '패션잡화': 0.8,
                '화장품': 0.8,
                '도서': 0.9,
                '스포츠/레저': 0.9,
                '문구/취미': 0.7
            },
        }

# 테스트 사용자 생성
        test_users = [
            # 10대 테스트 사용자
            {'username': 'male_10_low', 'gender': 'M', 'age': '10', 'income': 'L'},
            {'username': 'male_10_mid', 'gender': 'M', 'age': '10', 'income': 'M'},
            {'username': 'male_10_high', 'gender': 'M', 'age': '10', 'income': 'H'},
            {'username': 'female_10_low', 'gender': 'F', 'age': '10', 'income': 'L'},
            {'username': 'female_10_mid', 'gender': 'F', 'age': '10', 'income': 'M'},
            {'username': 'female_10_high', 'gender': 'F', 'age': '10', 'income': 'H'},

            # 20대 테스트 사용자
            {'username': 'male_20_low', 'gender': 'M', 'age': '20', 'income': 'L'},
            {'username': 'male_20_mid', 'gender': 'M', 'age': '20', 'income': 'M'},
            {'username': 'male_20_high', 'gender': 'M', 'age': '20', 'income': 'H'},
            {'username': 'female_20_low', 'gender': 'F', 'age': '20', 'income': 'L'},
            {'username': 'female_20_mid', 'gender': 'F', 'age': '20', 'income': 'M'},
            {'username': 'female_20_high', 'gender': 'F', 'age': '20', 'income': 'H'},

            # 30대 테스트 사용자
            {'username': 'male_30_low', 'gender': 'M', 'age': '30', 'income': 'L'},
            {'username': 'male_30_mid', 'gender': 'M', 'age': '30', 'income': 'M'},
            {'username': 'male_30_high', 'gender': 'M', 'age': '30', 'income': 'H'},
            {'username': 'female_30_low', 'gender': 'F', 'age': '30', 'income': 'L'},
            {'username': 'female_30_mid', 'gender': 'F', 'age': '30', 'income': 'M'},
            {'username': 'female_30_high', 'gender': 'F', 'age': '30', 'income': 'H'},

            # 40대 테스트 사용자
            {'username': 'male_40_low', 'gender': 'M', 'age': '40', 'income': 'L'},
            {'username': 'male_40_mid', 'gender': 'M', 'age': '40', 'income': 'M'},
            {'username': 'male_40_high', 'gender': 'M', 'age': '40', 'income': 'H'},
            {'username': 'female_40_low', 'gender': 'F', 'age': '40', 'income': 'L'},
            {'username': 'female_40_mid', 'gender': 'F', 'age': '40', 'income': 'M'},
            {'username': 'female_40_high', 'gender': 'F', 'age': '40', 'income': 'H'},

            # 50대 테스트 사용자
            {'username': 'male_50_low', 'gender': 'M', 'age': '50', 'income': 'L'},
            {'username': 'male_50_mid', 'gender': 'M', 'age': '50', 'income': 'M'},
            {'username': 'male_50_high', 'gender': 'M', 'age': '50', 'income': 'H'},
            {'username': 'female_50_low', 'gender': 'F', 'age': '50', 'income': 'L'},
            {'username': 'female_50_mid', 'gender': 'F', 'age': '50', 'income': 'M'},
            {'username': 'female_50_high', 'gender': 'F', 'age': '50', 'income': 'H'},
        ]

        # 카테고리와 상품 생성
        self.stdout.write('카테고리와 상품 생성 중...')
        for category_data in categories_data:
            category, _ = ProductCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': f'{category_data["name"]} 카테고리입니다.'}
            )
            
            for product_data in category_data['products']:
                Product.objects.get_or_create(
                    title=product_data['name'],
                    defaults={
                        'description': product_data.get('description', f'{product_data["name"]} 상품입니다.'),
                        'price': product_data['price'],
                        'theme': category.name,
                        'category': category,
                        'stock': random.randint(10, 100)
                    }
                )

        # 테스트 사용자 생성
        self.stdout.write('테스트 사용자 생성 중...')
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': f"{user_data['username']}@example.com",
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                
                # 사용자 프로필 생성
                profile = UserProfile.objects.create(
                    user=user,
                    gender=user_data['gender'],
                    age_group=user_data['age'],
                    income_level=user_data['income']
                )

                # 초기 행동 데이터 생성
                preferences = user_preferences[(user_data['gender'], user_data['age'], user_data['income'])]
                
                for category_name, preference_score in preferences.items():
                    category_products = Product.objects.filter(category__name=category_name)
                    
                    for product in category_products:
                        # 선호도에 따라 클릭 수와 체류 시간 설정
                        if random.random() < preference_score:
                            UserBehavior.objects.create(
                                user=user,
                                product=product,
                                view_duration=random.randint(30, 300),
                                click_count=random.randint(1, 5) if random.random() < preference_score else 0,
                                cart_add_count=1 if random.random() < preference_score * 0.5 else 0,
                                purchase_count=1 if random.random() < preference_score * 0.3 else 0
                            )

        self.stdout.write(self.style.SUCCESS('스테레오타입 데이터 생성 완료!'))