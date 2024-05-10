from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    password=serializers.CharField(max_length=100)
class FCMSerializer(serializers.Serializer):
    token=serializers.CharField(max_length=500)

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model=Alert
        fields=['id','name','price','image','slug']

class ForgotSerializer(serializers.Serializer):
    email=serializers.EmailField()
class ResetSerializer(serializers.Serializer):
    token=serializers.CharField(max_length=100)
    password=serializers.CharField(max_length=100)
    
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=Contact

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
           
            )
    class Meta:
        model=User
        fields=['username','password','email']

    def validate(self, attrs):
        if len(attrs['password'])<8:
            raise serializers.ValidationError({"password": "Password must be greater or equal to 8 characters"})
        elif User.objects.filter(username=attrs['username'].title()).exists():
            raise serializers.ValidationError({"username": "User already exists with this username"})
        elif User.objects.filter(email=attrs['email'].lower()).exists():
            raise serializers.ValidationError({"email": "User already exists with this email"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'].title(),
            email=validated_data['email'].lower(),
        )

        
        user.set_password(validated_data['password'])
        user.save()
        
        return user