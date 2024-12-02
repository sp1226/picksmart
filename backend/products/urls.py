# products/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
# products/urls.py
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('user-activity/', include([
        path('viewed/', views.ViewedProductsView.as_view(), name='viewed-products'),
        path('favorites/', views.FavoriteProductsView.as_view(), name='favorite-products'),
        path('reviews/', views.UserReviewsView.as_view(), name='user-reviews'),
        path('viewed/<int:pk>/', views.ViewedProductsView.as_view(), name='delete-viewed'),
        path('reviews/<int:pk>/', views.UserReviewsView.as_view(), name='delete-review'),
    ])),
]