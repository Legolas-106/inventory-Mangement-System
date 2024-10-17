from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, TokenSerializer, LoginSerializer
import logging

logger = logging.getLogger('login')


# User registration view
@api_view(['POST'])
def register(request):
    try:
        if request.method == 'POST':
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"User {user.username} registered successfully.")
                
                token = TokenSerializer.get_token(user)
                return Response({
                    "message": "User created successfully",
                    "access_token": f"{token['access']}"
                }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Registration failed with errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.critical(f"An error occurred during user registration: {str(e)}", exc_info=True)
        return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login view to authenticate users and retrieve JWT tokens
@api_view(['POST'])
def login(request):
    try:
        if request.method == 'POST':
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.data['username']
                password = request.data['password']
                user = authenticate(request, username=username, password=password)

                if user is not None:
                    logger.info(f"User {user.username} authenticated successfully.")
                    token_data = TokenSerializer.get_token(user)
                    return Response(token_data, status=status.HTTP_200_OK)
                else:
                    logger.warning(f"Login failed: Invalid credentials for username {username}")
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                logger.warning(f"Login failed with errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.critical(f"An error occurred during login: {str(e)}", exc_info=True)
        return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View for refreshing token or retrieving a new token
@api_view(['POST'])
def token_retrieve(request):
    try:
        user = request.user
        if user.is_authenticated:
            logger.info(f"User {user.username} requested token retrieval.")
            token_data = TokenSerializer.get_token(user)
            return Response(token_data, status=status.HTTP_200_OK)
        else:
            logger.warning("Token retrieval failed: User is not authenticated.")
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.critical(f"An error occurred during token retrieval: {str(e)}", exc_info=True)
        return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)