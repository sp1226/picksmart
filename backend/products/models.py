# backend/products/models.py
from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    theme = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    total_views = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    
    # 썸네일 자동 생성 필드 추가
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(width=600, height=600)],
        format='JPEG',
        options={'quality': 90}
    )
    list_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(width=300, height=300)],
        format='JPEG',
        options={'quality': 90}
    )

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class UserBehavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    view_duration = models.FloatField(default=0)
    click_count = models.IntegerField(default=0)
    cart_add_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)  # 추가
    review_score = models.FloatField(default=0)  # 추가
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product']

class ProductView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    view_duration = models.IntegerField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']

class UserProductRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']

class ProductFavorite(models.Model):
    """찜한 상품"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username}'s favorite: {self.product.title}"

class RecommendationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()
    recommended_at = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-recommended_at']
        
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']
        
    def __str__(self):
        return f"{self.user.username}'s review on {self.product.title}"
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username}'s cart - {self.product.title}"