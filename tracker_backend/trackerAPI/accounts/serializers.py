from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'income', )

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(style={'input_type': 'username'}, required=True)
    password = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if user:
            pass
        else:
            raise ValidationError('Unable to login with provided credentials.')

        return user

    class Meta:
        model = User
        fields = ('username', 'password', )

class SignupSerializer(serializers.Serializer):

    # JSON fields rendered for response body
    id = serializers.ReadOnlyField()
    username = serializers.CharField(style={'input_type': 'username'}, required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.CharField(style={'input_type': 'email'}, required=True)
    income = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def create(self, validated_data):
        try:
            user = User.objects.get(username__iexact=self.validated_data['username'])
        except User.DoesNotExist:
            user = UserSerializer.create(self, validated_data)
            user.set_password(validated_data['password'])

            user.save()

            return user

        raise ValidationError('Username already in use.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', )