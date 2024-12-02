from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from products.models import (
    ProductCategory, ProductFavorite, ProductView, RecommendationLog,
    UserProductRating, Product, UserBehavior, CartItem
)
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, FloatField, Q, Max, Case, When
from django.db.models.functions import Coalesce, Cast, Greatest, ExtractHour, ExtractMonth, TruncMonth
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from products.serializers import ProductSerializer, ReviewSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                profile = user.userprofile
                user_data = {
                    'username': user.username,
                    'gender': profile.gender,
                    'age_group': profile.age_group,
                    'income_level': profile.income_level
                }
            except UserProfile.DoesNotExist:
                user_data = {'username': user.username}
            return Response({'status': 'success', 'user': user_data})
        return Response({'status': 'error', 'message': '로그인에 실패했습니다.'}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LogoutView(APIView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'status': 'success', 'message': '로그아웃되었습니다.'})
        return Response({'status': 'error', 'message': '로그인 상태가 아닙니다.'}, status=status.HTTP_400_BAD_REQUEST)

class CheckLoginStatusView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = []  # 권한 체크 해제

    def get(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                user_data = {
                    'username': request.user.username,
                    'gender': profile.gender,
                    'age_group': profile.age_group,
                    'mileage': profile.mileage
                }
            except UserProfile.DoesNotExist:
                user_data = {
                    'username': request.user.username
                }
            return Response({
                'isAuthenticated': True,
                'user': user_data
            })
        return Response({
            'isAuthenticated': False,
            'user': None
        })
        
@method_decorator(ensure_csrf_cookie, name='dispatch')
class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        gender = request.data.get('gender')
        age_group = request.data.get('age_group')
        income_level = request.data.get('income_level')

        if not username or not password:
            return Response({'status': 'error', 'message': '사용자명과 비밀번호는 필수입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'status': 'error', 'message': '이미 존재하는 사용자명입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        user.save()

        UserProfile.objects.create(user=user, gender=gender, age_group=age_group, income_level=income_level)

        return Response({'status': 'success', 'message': '회원가입이 완료되었습니다.', 'user': {'username': username}})


class UserProfileView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = []

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'user': None,
                    'is_authenticated': False,
                    'activity_stats': {
                        'total_views': 0,
                        'favorite_count': 0,
                        'cart_count': 0,
                        'review_count': 0
                    },
                    'category_preferences': []
                })

            user = request.user
            profile = user.userprofile

            # UserProfile에서 mileage 필드 사용
            user_data = {
                'username': user.username,
                'gender': profile.gender,
                'age_group': profile.age_group,
                'income_level': profile.income_level,
                'mileage': profile.mileage,
            }

            # 사용자 활동 통계 계산
            activity_stats = {
                'total_views': ProductView.objects.filter(user=user).count(),
                'favorite_count': ProductFavorite.objects.filter(user=user).count(),
                'cart_count': CartItem.objects.filter(user=user).count(),
                'review_count': UserProductRating.objects.filter(user=user).count()
            }

            # 카테고리 선호도 계산
            categories = ProductCategory.objects.all()
            category_preferences = []
            total_score = 0

            # 첫 번째 패스: 모든 카테고리의 점수 합계 계산
            for category in categories:
                behavior_data = UserBehavior.objects.filter(user=user, product__category=category).aggregate(
                    view_duration=Coalesce(Cast(Sum('view_duration'), FloatField()), 0.0),
                    clicks=Coalesce(Cast(Sum('click_count'), FloatField()), 0.0),
                    cart_adds=Coalesce(Cast(Sum('cart_add_count'), FloatField()), 0.0),
                    purchases=Coalesce(Cast(Sum('purchase_count'), FloatField()), 0.0)
                )
                
                behavior_score = (
                    float(behavior_data['view_duration']) * 0.3 +
                    float(behavior_data['clicks']) * 0.5 +
                    float(behavior_data['cart_adds']) * 1.0 +
                    float(behavior_data['purchases']) * 2.0
                )
                
                view_score = float(ProductView.objects.filter(user=user, product__category=category).aggregate(
                    total_duration=Coalesce(Cast(Sum('view_duration'), FloatField()), 0.0)
                )['total_duration'])
                
                rec_score = float(RecommendationLog.objects.filter(
                    user=user, product__category=category, clicked=True
                ).aggregate(
                    avg_score=Coalesce(Cast(Avg('score'), FloatField()), 0.0)
                )['avg_score'])
                
                rating_score = float(UserProductRating.objects.filter(
                    user=user, product__category=category
                ).aggregate(
                    avg_rating=Coalesce(Cast(Avg('rating'), FloatField()), 0.0)
                )['avg_rating'])

                total_category_score = (
                    behavior_score * 0.4 +
                    view_score * 0.2 +
                    rec_score * 0.2 +
                    rating_score * 0.2
                )

                if total_category_score > 0:
                    category_preferences.append({
                        'name': category.name,
                        'total_score': total_category_score
                    })
                    total_score += total_category_score

            # 두 번째 패스: 백분율 계산
            normalized_preferences = []
            if total_score > 0:
                for pref in category_preferences:
                    percentage = (pref['total_score'] / total_score) * 100
                    normalized_preferences.append({
                        'category': pref['name'],
                        'score': round(percentage, 1)
                    })
            
            # 점수 기준 내림차순 정렬
            normalized_preferences.sort(key=lambda x: x['score'], reverse=True)

            return Response({
                'user': user_data,
                'is_authenticated': True,
                'category_preferences': normalized_preferences,
                'activity_stats': activity_stats
            })

        except UserProfile.DoesNotExist:
            return Response({'error': '사용자 프로필을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Profile view error: {str(e)}")
            return Response({'error': '사용자 데이터를 불러오는 중 오류가 발생했습니다.', 'is_authenticated': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)  # 최근 30일 데이터
        
        # 시간대별 쇼핑 패턴
        time_patterns = (
            ProductView.objects.filter(
                user=user,
                viewed_at__range=(start_date, end_date)
            ).extra(
                select={'hour': "EXTRACT(hour FROM viewed_at)"}
            ).values('hour').annotate(
                views=Count('id')
            ).order_by('hour')
        )

        # 상호작용 통계
        interaction_stats = {
            'views': ProductView.objects.filter(user=user).count(),
            'purchases': UserBehavior.objects.filter(
                user=user, purchase_count__gt=0
            ).count(),
            'cart_adds': UserBehavior.objects.filter(
                user=user, cart_add_count__gt=0
            ).count(),
        }

        # 카테고리별 평점 분석
        rating_analysis = (
            UserProductRating.objects.filter(user=user)
            .values('product__category__name')
            .annotate(
                avg_rating=Avg('rating'),
                review_count=Count('id')
            )
        )

        # 구매 패턴 (월별)
        purchase_patterns = (
            UserBehavior.objects.filter(
                user=user,
                purchase_count__gt=0
            ).extra(
                select={'month': "EXTRACT(month FROM last_viewed)"}
            ).values('month').annotate(
                amount=Count('id')
            ).order_by('month')
        )

        return Response({
            'timePatterns': list(time_patterns),
            'interactionStats': [
                {'name': key, 'value': value}
                for key, value in interaction_stats.items()
            ],
            'ratingAnalysis': list(rating_analysis),
            'purchasePatterns': list(purchase_patterns)
        })

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = []

    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})
