from django.db.models import Sum, F, ExpressionWrapper, FloatField, Q
from products.models import ( UserBehavior, ProductView, UserProductRating, ProductFavorite)
from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.db.models import FloatField
from django.db.models.functions import Cast
from django.utils import timezone  # timezone import 추가
from datetime import timedelta  # timedelta import 추가


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    )

    AGE_GROUP_CHOICES = (
        ('10', '10대'),
        ('20', '20대'),
        ('30', '30대'),
        ('40', '40대'),
        ('50', '50대 이상'),
    )

    INCOME_LEVEL_CHOICES = (
        ('L', '저소득'),
        ('M', '중소득'),
        ('H', '고소득'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age_group = models.CharField(max_length=2, choices=AGE_GROUP_CHOICES)
    income_level = models.CharField(max_length=1, choices=INCOME_LEVEL_CHOICES)
    mileage = models.DecimalField(max_digits=12, decimal_places=2, default=10000000)  # 1000만원 기본값
    preferred_categories = models.ManyToManyField('products.ProductCategory', blank=True)  # 문자열로 참조
    dummy_field = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_activity_stats(self):
        """사용자 활동 통계 반환"""

        # 조회수 계산
        total_views = ProductView.objects.filter(user=self.user).count()

        # 찜한 상품 수
        favorite_count = ProductFavorite.objects.filter(user=self.user).count()

        # 장바구니에 담은 상품 수
        cart_count = UserBehavior.objects.filter(
            user=self.user,
            cart_add_count__gt=0
        ).count()

        # 리뷰 수
        review_count = UserProductRating.objects.filter(user=self.user).count()

        return {
            'total_views': total_views,
            'favorite_count': favorite_count,
            'cart_count': cart_count,
            'review_count': review_count
        }
    


    def update_preferred_categories(self):
        """사용자의 행동 데이터를 기반으로 선호 카테고리 업데이트"""
        try:
            print(f"\nUpdating preferences for user: {self.user.username}")
            
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            category_scores = UserBehavior.objects.filter(
                user=self.user,
                product__category__isnull=False,
                last_viewed__gte=thirty_days_ago
            ).values(
                'product__category',
                'product__category__name'
            ).annotate(
                view_score=ExpressionWrapper(
                    Cast(Sum('view_duration'), FloatField()) * 0.3,
                    output_field=FloatField()
                ),
                click_score=ExpressionWrapper(
                    Cast(Sum('click_count'), FloatField()) * 0.5,
                    output_field=FloatField()
                ),
                cart_score=ExpressionWrapper(
                    Cast(Sum('cart_add_count'), FloatField()) * 1.5,  # 장바구니 가중치 증가
                    output_field=FloatField()
                ),
                purchase_score=ExpressionWrapper(
                    Cast(Sum('purchase_count'), FloatField()) * 2.0,
                    output_field=FloatField()
                ),
                total_score=ExpressionWrapper(
                    Cast(Sum('view_duration'), FloatField()) * 0.3 +
                    Cast(Sum('click_count'), FloatField()) * 0.5 +
                    Cast(Sum('cart_add_count'), FloatField()) * 1.5 +  # 장바구니 가중치 증가
                    Cast(Sum('purchase_count'), FloatField()) * 2.0,
                    Cast(Sum('favorite_count'), FloatField()) * 1.0 +  # 찜하기 점수
                    Cast(Sum('review_score'), FloatField()) * 1.0,    # 리뷰 점수

                    output_field=FloatField()
                )
            ).order_by('-total_score')

            print("\nCategory scores calculated:")
            for score in category_scores:
                print(f"Category: {score['product__category__name']}")
                print(f"- View Score: {score.get('view_score', 0):.2f}")
                print(f"- Click Score: {score.get('click_score', 0):.2f}")
                print(f"- Cart Score: {score.get('cart_score', 0):.2f}")
                print(f"- Purchase Score: {score.get('purchase_score', 0):.2f}")
                print(f"- Total Score: {score.get('total_score', 0):.2f}")

            # 기존 선호도 제거
            self.preferred_categories.clear()

            # 상위 5개 카테고리 선정 및 추가
            ProductCategory = apps.get_model('products', 'ProductCategory')
            for score in category_scores[:5]:
                if score['product__category'] is not None:
                    try:
                        category = ProductCategory.objects.get(id=score['product__category'])
                        self.preferred_categories.add(category)
                        print(f"Added preferred category: {category.name} (Score: {score.get('total_score', 0):.2f})")
                    except ProductCategory.DoesNotExist:
                        print(f"Category {score['product__category']} not found")

            print("\nPreference update completed successfully")
            return True

        except Exception as e:
            print(f"Error updating preferences: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
