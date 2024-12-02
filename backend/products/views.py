# products/views.py
from .models import Product, ProductView, UserBehavior, UserProductRating, ProductFavorite, RecommendationLog, CartItem
from .serializers import ProductSerializer
from .serializers import CartItemSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, F, Q, Max, Case, When, Value, DateTimeField, Subquery, OuterRef
from django.db.models.functions import Greatest, Coalesce
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .services import RecommendationService 
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
import pytz
import logging
from decimal import Decimal  # 상단에 추가

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    상품 관련 ViewSet
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['DELETE'])
    def viewed(self, request, pk=None):
        """최근 본 상품 삭제"""
        try:
            ProductView.objects.filter(
                user=request.user,
                product_id=pk
            ).delete()
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['DELETE'])
    def reviews(self, request, pk=None):
        """리뷰 삭제"""
        try:
            UserProductRating.objects.filter(
                user=request.user,
                id=pk
            ).delete()
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def get_permissions(self):
        if self.action in ['add_to_cart', 'check_cart']:
            return [IsAuthenticated()]
        return super().get_permissions()


    @action(detail=True, methods=['POST'])
    def log_interaction(self, request, pk=None):
        """사용자 상품 상호작용 로깅"""
        try:
            product = self.get_object()
            interaction_type = request.data.get('type', '')
            duration = request.data.get('duration', 0)
            
            try:
                duration = float(duration)
            except (TypeError, ValueError):
                duration = 0.0

            with transaction.atomic():
                # **추가: 디버깅 로그로 데이터 확인**
                print(f"[DEBUG] Logging interaction for user {request.user}, product {product}, duration {duration}")
                
                # 조회수 증가
                Product.objects.filter(id=product.id).update(total_views=F('total_views') + 1)
                
                if request.user.is_authenticated:
                    # 조회 기록 생성
                    ProductView.objects.create(
                        user=request.user,
                        product=product,
                        view_duration=int(duration)
                    )

                    # 행동 데이터 업데이트
                    behavior, created = UserBehavior.objects.get_or_create(
                        user=request.user,
                        product=product,
                        defaults={
                            'view_duration': duration,
                            'click_count': 1,
                            'cart_add_count': 0,
                            'purchase_count': 0,
                            'last_viewed': timezone.now()
                        }
                    )
                    if not created:
                        behavior.view_duration += duration
                        behavior.click_count += 1
                        behavior.last_viewed = timezone.now()
                        behavior.save()
                        
            return Response({'status': 'success'})
            
        except Exception as e:
            print(f"[ERROR] Failed to log interaction: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['POST'])
    def toggle_favorite(self, request, pk=None):
        """상품 찜 상태 토글"""
        try:
            if not request.user.is_authenticated:
                return Response({'error': '로그인이 필요한 서비스입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

            product = self.get_object()
            favorite = ProductFavorite.objects.filter(user=request.user, product=product).first()

            if favorite:
                favorite.delete()
                message = '찜하기가 취소되었습니다.'
                is_favorited = False
            else:
                ProductFavorite.objects.create(user=request.user, product=product)
                message = '상품을 찜했습니다.'
                is_favorited = True

            # **추가: 상태 확인 디버깅 로그**
            print(f"[DEBUG] Favorite toggled for user {request.user}, product {product}, is_favorited: {is_favorited}")
            
            return Response({
                'status': 'favorited' if is_favorited else 'unfavorited',
                'message': message,
                'is_favorited': is_favorited
            })

        except Exception as e:
            print(f"[ERROR] Toggle favorite error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def add_review(self, request, pk=None):
        """리뷰 추가"""
        try:
            if not request.user.is_authenticated:
                return Response({'error': '로그인이 필요한 서비스입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

            product = self.get_object()
            rating = request.data.get('rating')
            content = request.data.get('content', '')

            # **추가: 유효성 검사 디버깅 로그**
            print(f"[DEBUG] Add review for user {request.user}, product {product}, rating {rating}, content: {content}")

            try:
                rating = int(rating)
            except (TypeError, ValueError):
                return Response({'error': '평점은 1-5 사이의 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

            if not (1 <= rating <= 5):
                return Response({'error': '평점은 1-5 사이의 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

            # 리뷰 생성 또는 업데이트
            rating_obj, created = UserProductRating.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'content': content
                }
            )

            # 평균 평점 업데이트
            avg_rating = UserProductRating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.average_rating = avg_rating or 0
            product.save()

            return Response({
                'status': 'success',
                'average_rating': product.average_rating,
                'message': '리뷰가 등록되었습니다.'
            })

        except Exception as e:
            print(f"[ERROR] Add review error: {str(e)}")
            return Response({'error': '리뷰 등록 중 오류가 발생했습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def reviews(self, request, pk=None):
        """상품 리뷰 목록 조회"""
        try:
            product = self.get_object()
            reviews = UserProductRating.objects.filter(product=product)\
                .select_related('user')\
                .order_by('-created_at')  # 최신순 정렬
            
            review_data = []
            for review in reviews:
                review_data.append({
                    'id': review.id,
                    'user': review.user.username,
                    'rating': review.rating,
                    'content': review.content,  # 리뷰 내용 포함
                    'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
                })
                
            return Response(review_data)
            
        except Exception as e:
            print(f"Error fetching reviews: {str(e)}")
            return Response(
                {'error': '리뷰를 불러오는 중 오류가 발생했습니다.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
                    
    @action(detail=True, methods=['GET'])
    def check_cart(self, request, pk=None):
        """장바구니 상태 확인"""
        try:
            product = self.get_object()
            if not request.user.is_authenticated:
                return Response({
                    'in_cart': False
                })
                
            # CartItem 테이블에서 확인
            in_cart = CartItem.objects.filter(
                user=request.user,
                product=product
            ).exists()
            
            return Response({
                'in_cart': in_cart
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def update_cart_quantity(self, request, pk=None):
        try:
            quantity = int(request.data.get('quantity', 1))
            if quantity < 1:
                return Response(
                    {'error': '수량은 1 이상이어야 합니다.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            behavior, created = UserBehavior.objects.get_or_create(
                user=request.user,
                product_id=pk,
                defaults={'cart_add_count': quantity}
            )
            
            if not created:
                behavior.cart_add_count = quantity
                behavior.save()

            return Response({
                'status': 'success',
                'quantity': quantity,
                'total_price': float(behavior.product.price * quantity)
            })

        except Product.DoesNotExist:
            return Response(
                {'error': '상품을 찾을 수 없습니다.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error updating cart quantity: {str(e)}")
            return Response(
                {'error': '수량 변경에 실패했습니다.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

            
    @action(detail=True, methods=['POST', 'DELETE'])  # DELETE 메서드 추가
    def remove_from_cart(self, request, pk=None):
        """장바구니에서 제거"""
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': '로그인이 필요한 서비스입니다.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            product = self.get_object()
            
            # CartItem에서 제거
            CartItem.objects.filter(
                user=request.user,
                product=product
            ).delete()

            return Response({
                'status': 'success',
                'message': '장바구니에서 제거되었습니다.'
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

                
    @action(detail=False, methods=['GET'])
    def themes(self, request):
        """테마별 상품 목록 제공"""
        try:
            themes = {
                '전자기기': Product.objects.filter(theme='전자기기'),
                '패션잡화': Product.objects.filter(theme='패션잡화'),
                '화장품': Product.objects.filter(theme='화장품'),
                '도서': Product.objects.filter(theme='도서'),
                '스포츠/레저': Product.objects.filter(theme='스포츠/레저'),
                '문구/취미': Product.objects.filter(theme='문구/취미')
            }
            
            response_data = []
            for theme_name, products in themes.items():
                if products.exists():
                    serializer = ProductSerializer(products, many=True)
                    response_data.append({
                        'title': theme_name,
                        'products': serializer.data
                    })
            
            return Response(response_data)
                
        except Exception as e:
            print(f"Themes endpoint error: {str(e)}")
            return Response(
                {'error': '테마 데이터를 불러오는데 실패했습니다.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def recommendations(self, request):
        try:
            limit = int(request.query_params.get('limit', 8))
            current_id = request.query_params.get('current_id')
            
            if current_id:
                try:
                    current_product = Product.objects.get(id=current_id)
                    
                    # 로그인한 사용자의 경우 선호도 기반 추천
                    if request.user.is_authenticated:
                        recommendation_service = RecommendationService(request.user)
                        
                        # 현재 상품을 제외한 모든 상품에 대해 예측 점수 계산
                        all_products = Product.objects.exclude(id=current_id)
                        predictions = []
                        
                        for product in all_products:
                            try:
                                score = recommendation_service.predict_user_interest(product.id)
                                # 같은 카테고리 상품에 약간의 가중치 부여
                                if product.category == current_product.category:
                                    score *= 1.2
                                predictions.append((product, score))
                            except Exception as e:
                                print(f"Error predicting for product {product.id}: {str(e)}")
                                continue
                        
                        # 예측 점수로 정렬하고 랜덤성 추가
                        predictions.sort(key=lambda x: (x[1] + random.random() * 0.2), reverse=True)
                        recommended_products = [pred[0] for pred in predictions[:limit]]
                        
                    else:
                        # 비로그인 사용자를 위한 랜덤 추천
                        # 현재 카테고리에서 60%, 다른 카테고리에서 40%
                        same_category_limit = int(limit * 0.6)
                        other_category_limit = limit - same_category_limit
                        
                        # 같은 카테고리에서 랜덤 선택
                        same_category_products = list(
                            Product.objects.filter(category=current_product.category)
                            .exclude(id=current_id)
                            .order_by('?')[:same_category_limit]
                        )
                        
                        # 다른 카테고리에서 랜덤 선택
                        other_products = list(
                            Product.objects.exclude(category=current_product.category)
                            .exclude(id=current_id)
                            .order_by('?')[:other_category_limit]
                        )
                        
                        recommended_products = same_category_products + other_products
                        random.shuffle(recommended_products)  # 최종 결과 섞기
                    
                    serializer = self.get_serializer(recommended_products, many=True)
                    return Response(serializer.data)
                    
                except Product.DoesNotExist:
                    return Response({"error": "Current product not found"}, status=404)
                    
            else:
                # 일반 추천 로직 (기존과 동일)
                if not request.user.is_authenticated:
                    products = Product.objects.all().order_by('?')[:limit]
                    serializer = self.get_serializer(products, many=True)
                    return Response(serializer.data)

                recommendation_service = RecommendationService(request.user)
                recommended_products = recommendation_service.get_recommendations(limit=limit)
                serializer = self.get_serializer(recommended_products, many=True)
                return Response(serializer.data)
                        
        except Exception as e:
            print(f"Recommendation error: {str(e)}")
            products = Product.objects.all().order_by('?')[:limit]
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
            
    @action(detail=True, methods=['GET'])
    def check_review(self, request, pk=None):
        """현재 사용자의 해당 상품 리뷰 존재 여부 확인"""
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': '로그인이 필요한 서비스입니다.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            product = self.get_object()
            review = UserProductRating.objects.filter(
                user=request.user,
                product=product
            ).first()

            if review:
                return Response({
                    'hasReview': True,
                    'review': {
                        'rating': review.rating,
                        'content': review.content,
                        'created_at': review.created_at
                    }
                })
            return Response({'hasReview': False})

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    
    def get_queryset(self):
        # 현재 로그인한 사용자의 장바구니 아이템만 반환
        return CartItem.objects.filter(user=self.request.user)
        
    def get_serializer_class(self):
        return CartItemSerializer
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_multiple(self, request):
        """여러 상품을 장바구니에 한 번에 추가"""
        try:
            product_ids = request.data.get('productIds', [])
            
            if not isinstance(product_ids, list):
                return Response(
                    {"error": "올바르지 않은 상품 목록입니다"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            added_products = []
            failed_products = []
            
            with transaction.atomic():
                for product_id in product_ids:
                    try:
                        # 상품 존재 확인
                        product = Product.objects.get(id=product_id)
                        
                        # 재고 확인
                        if product.stock <= 0:
                            failed_products.append({
                                "product_id": product_id,
                                "error": "재고가 부족합니다"
                            })
                            continue
                        
                        # 장바구니에 이미 있는지 확인 후 추가 또는 업데이트
                        cart_item, created = CartItem.objects.get_or_create(
                            user=request.user,
                            product=product,
                            defaults={'quantity': 1}
                        )
                        
                        if not created:
                            # 이미 장바구니에 있으면 수량만 1 증가
                            cart_item.quantity += 1
                            cart_item.save()
                        
                        added_products.append(product_id)
                        
                    except Product.DoesNotExist:
                        failed_products.append({
                            "product_id": product_id,
                            "error": "상품을 찾을 수 없습니다"
                        })
                    except Exception as e:
                        failed_products.append({
                            "product_id": product_id,
                            "error": str(e)
                        })
            
            # 모든 처리가 완료된 후 응답
            if added_products:
                return Response({
                    "status": "success",
                    "message": "선택한 상품이 장바구니에 추가되었습니다",
                    "added_products": added_products,
                    "failed_products": failed_products
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "장바구니에 추가할 수 있는 상품이 없습니다",
                    "failed_products": failed_products
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"장바구니 추가 중 오류가 발생했습니다: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

    @action(detail=False, methods=['GET'])
    def my_cart(self, request):
        """사용자의 장바구니 목록 조회"""
        try:
            # request.user 대신 self.request.user를 사용할 수도 있음
            cart_items = CartItem.objects.filter(user=request.user)
            data = []
            
            for item in cart_items:
                product_data = ProductSerializer(item.product).data
                data.append({
                    'id': item.id,
                    'product': product_data,
                    'quantity': item.quantity,
                    'total_price': float(item.product.price) * item.quantity,
                    'added_at': item.added_at
                })

            return Response(data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    

    @action(detail=True, methods=['POST'])
    def add_to_cart(self, request, pk=None):
        """장바구니에 추가"""
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': '로그인이 필요한 서비스입니다.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            product = self.get_object()
            
            # CartItem 생성 또는 업데이트
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': 1}
            )
            
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            # UserBehavior 업데이트
            behavior, _ = UserBehavior.objects.get_or_create(
                user=request.user,
                product=product
            )
            behavior.cart_add_count += 1
            behavior.save()
            
            serializer = CartItemSerializer(cart_item)

            return Response({
                'status': 'success',
                'message': {'detail': '장바구니에 추가되었습니다.'},
                'cart_item': serializer.data
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        
    @action(detail=True, methods=['PATCH'])  
    def update_quantity(self, request, pk=None):
        """장바구니 상품 수량 업데이트"""
        try:
            cart_item = CartItem.objects.get(
                user=request.user,
                product_id=pk
            )
            
            quantity = int(request.data.get('quantity', 1))
            
            # 재고 확인
            if cart_item.product.stock < quantity:
                return Response({
                    'error': '재고가 부족합니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            cart_item.quantity = quantity
            cart_item.save()
            
            return Response({
                'message': '수량이 업데이트되었습니다.',
                'quantity': cart_item.quantity
            })
            
        except CartItem.DoesNotExist:
            return Response({
                'error': '장바구니에 해당 상품이 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['DELETE'])
    def remove_item(self, request, pk=None):
        """장바구니에서 상품 제거"""
        try:
            result = CartItem.objects.filter(
                user=request.user,
                product_id=pk
            ).delete()
            
            if result[0] == 0:  # 삭제된 항목이 없음
                return Response({
                    'error': '장바구니에 해당 상품이 없습니다.'
                }, status=status.HTTP_404_NOT_FOUND)
                
            return Response({
                'message': '상품이 장바구니에서 제거되었습니다.'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['DELETE'])
    def clear(self, request):
        """장바구니 비우기"""
        try:
            CartItem.objects.filter(user=request.user).delete()
            return Response({
                'message': '장바구니가 비워졌습니다.'
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
                    


    @action(detail=True, methods=['GET'])
    def check_cart_status(self, request, pk=None):
        """장바구니 상태 확인"""
        try:
            if not request.user.is_authenticated:
                return Response({'in_cart': False})

            product = self.get_object()
            in_cart = UserBehavior.objects.filter(
                user=request.user,
                product=product,
                cart_add_count__gt=0
            ).exists()

            return Response({'in_cart': in_cart})

        except Exception as e:
            print(f"장바구니 상태 확인 중 오류 발생: {str(e)}")
            return Response({'in_cart': False})
                
    # 사용자 행동을 기록하는 함수
    def record_user_behavior(user, product, view_duration=0, click=False, cart_add=False, purchase=False):
        behavior, created = UserBehavior.objects.get_or_create(
            user=user,
            product=product,
            defaults={
                'view_duration': view_duration,
                'click_count': 1 if click else 0,
                'cart_add_count': 1 if cart_add else 0,
                'purchase_count': 1 if purchase else 0,
                'last_viewed': timezone.now(),
            }
        )

        if not created:
            behavior.view_duration += view_duration
            if click:
                behavior.click_count += 1
            if cart_add:
                behavior.cart_add_count += 1
            if purchase:
                behavior.purchase_count += 1
            behavior.last_viewed = timezone.now()
            behavior.save()
                
    @action(detail=False, methods=['POST'])
    def purchase(self, request):
        try:
            user = request.user
            print(f"[DEBUG] Purchase attempt by user: {user.username}")
            if not user.is_authenticated:
                return Response(
                    {'error': '로그인이 필요한 서비스입니다.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            with transaction.atomic():
                # 장바구니 아이템 조회
                cart_items = CartItem.objects.filter(user=user)
                print(f"[DEBUG] Cart items found: {cart_items.count()}")
                            
                if not cart_items.exists():
                    return Response(
                        {'error': '장바구니가 비어있습니다.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 총 구매 금액 계산
                total_amount = Decimal('0')
                for item in cart_items:
                    print(f"[DEBUG] Processing item: {item.product.title}, Quantity: {item.quantity}, Price: {item.product.price}")
                    total_amount += item.product.price * Decimal(str(item.quantity))

                # 사용자 마일리지 조회
                profile = user.userprofile
                if profile.mileage < total_amount:
                    return Response(
                        {'error': f'마일리지가 부족합니다. (보유: {profile.mileage:,}원, 필요: {total_amount:,}원)'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 마일리지 차감
                profile.mileage -= total_amount
                profile.save()

                # 구매 기록 생성 및 재고 체크/감소
                for item in cart_items:
                    # 재고 확인
                    if item.product.stock < item.quantity:
                        raise ValueError(f'{item.product.title}의 재고가 부족합니다.')
                    
                    # 재고 감소
                    item.product.stock -= item.quantity
                    item.product.save()
                    
                    # 구매 기록 생성 또는 업데이트
                    behavior, created = UserBehavior.objects.get_or_create(
                        user=user,
                        product=item.product,
                        defaults={
                            'purchase_count': item.quantity,
                            'view_duration': 0,
                            'click_count': 0,
                            'cart_add_count': 0,
                            'favorite_count': 0,
                            'review_score': 0,
                            'last_viewed': timezone.now()
                        }
                    )
                    
                    if not created:
                        behavior.purchase_count += item.quantity
                        behavior.save()

                # 장바구니 비우기
                cart_items.delete()

                return Response({
                    'message': '구매가 완료되었습니다.',
                    'total_amount': total_amount,
                    'remaining_mileage': profile.mileage
                })

        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"[ERROR] Purchase failed: {str(e)}")
            print(f"[ERROR] Error type: {type(e)}")
            import traceback
            print(traceback.format_exc())
            print(f"Purchase error: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class ViewedProductsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 12))
            offset = (page - 1) * page_size

            user = request.user
            products = Product.objects.filter(
                Q(productview__user=user) | 
                Q(userbehavior__user=user, userbehavior__view_duration__gt=0)
            ).annotate(
                latest_view=Max('productview__viewed_at')
            ).order_by('-latest_view').distinct()

            total_products = products.count()
            paginated_products = products[offset:offset + page_size]
            
            return Response({
                'results': ProductSerializer(paginated_products, many=True).data,
                'next': (offset + page_size) < total_products
            })

        except Exception as e:
            print(f"Error in ViewedProductsView: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FavoriteProductsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 12))
            offset = (page - 1) * page_size

            user = request.user
            products = Product.objects.filter(
                productfavorite__user=user
            ).order_by('-productfavorite__created_at')

            total_products = products.count()
            paginated_products = products[offset:offset + page_size]
            
            return Response({
                'results': ProductSerializer(paginated_products, many=True).data,
                'next': (offset + page_size) < total_products
            })

        except Exception as e:
            print(f"Error in FavoriteProductsView: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserReviewsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 12))
            offset = (page - 1) * page_size

            user = request.user
            reviews = UserProductRating.objects.filter(
                user=user
            ).select_related('product', 'user').order_by('-created_at')

            print(f"Found {reviews.count()} reviews for user {user}")  # 디버깅용 로그 추가

            total_reviews = reviews.count()
            paginated_reviews = reviews[offset:offset + page_size]

            serialized_data = [
                {
                    'id': review.id,
                    'rating': review.rating,
                    'content': review.content,
                    'created_at': review.created_at,
                    'product': ProductSerializer(review.product).data
                } for review in paginated_reviews
            ]

            return Response({
                'results': serialized_data,
                'next': (offset + page_size) < total_reviews
            })
            
        except Exception as e:
            print(f"Error in UserReviewsView: {str(e)}")
            print(f"Error details: {type(e).__name__}")  # 에러 타입 추가
            import traceback
            print(traceback.format_exc())  # 스택 트레이스 추가
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    
    
def create_paginated_response(queryset, page, page_size, serializer_class):

    offset = (page - 1) * page_size
    total_count = queryset.count()
    items = queryset[offset:offset + page_size]

    return {
        'count': total_count,
        'next': (offset + page_size) < total_count,
        'previous': page > 1,
        'results': serializer_class(items, many=True).data
    }