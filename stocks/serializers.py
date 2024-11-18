# stocks/serializers.py
from typing import OrderedDict
from rest_framework import serializers
from .models import * 


class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        write_only_fields = ['password']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = AuthUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user
    
class UserLoginSerializer(serializers.ModelSerializer):
        class Meta:
            model = AuthUser
            fields = ['username', 'password']
    
class UserPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    moderator_username = serializers.CharField(source='moderator.username', read_only=True)
    platform_commission = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ["id", "seller_username", "moderator_username", "status", "created_at", 
                  "formed_at", "completed_at", "rejected_at", "platform_commission"]
        
    def get_platform_commission(self, obj):
        # Возвращаем значение комиссии только если статус 'completed'
        if obj.status == 'completed':
            return obj.platform_commission
        return None

class ProductStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['completed', 'rejected'])
    
class CategoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ['product', 'category', 'is_main']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"  
        
      
    
    