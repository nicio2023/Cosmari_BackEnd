from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'firstname', 'lastname', 'password']

    def validate_email(self, value):
        if not value.endswith('@cosmari.it'):
            raise serializers.ValidationError("L'email deve essere un'email aziendale")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            password=validated_data['password']
        )
        return user