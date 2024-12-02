# backend/products/serializers.py
from rest_framework import serializers
from .models import Product, UserProductRating, ProductReview, CartItem
from accounts.models import UserProfile  # UserProfile을 accounts에서 import

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    list_thumbnail_url = serializers.SerializerMethodField()
    viewed_at = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price',
            'image_url', 'thumbnail_url', 'list_thumbnail_url',
            'theme', 'category', 'total_views', 
            'average_rating', 'stock', 'viewed_at'
        ]

    def get_viewed_at(self, obj):
        if not self.context.get('viewed_timestamps'):
            return None
        return self.context['viewed_timestamps'].get(obj.id)

    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.image:  # 썸네일이 없을 경우 원본 이미지 반환
            try:
                return obj.thumbnail.url
            except:
                return obj.image.url
        return None

    def get_list_thumbnail_url(self, obj):
        if obj.image:  # 리스트 썸네일이 없을 경우 썸네일이나 원본 이미지 반환
            try:
                return obj.list_thumbnail.url
            except:
                try:
                    return obj.thumbnail.url
                except:
                    return obj.image.url
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['gender', 'age_group', 'income_level', 'preferred_categories']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductRating
        fields = ['id', 'rating', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = ['id', 'rating', 'comment', 'created_at', 'username']
        
    def get_username(self, obj):
        return obj.user.username
    
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price', 'added_at']

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price