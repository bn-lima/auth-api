from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import RegisterAccountSerializer, LoginAccountSerializer, RefreshTokenSerializer

class RegisterAccountView(APIView): # Registra um usuário
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = RegisterAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "account created successfully"}, status=status.HTTP_201_CREATED)

class LoginAccountView(APIView): # Loga um usuário
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = LoginAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token, refresh_token = serializer.save()

        return Response( # Retorna refresh e access token na resposta
            {
                "message": "login was successfully",
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            status=status.HTTP_200_OK
        )

class RefreshTokenView(APIView): # Gera um novo token de acesso para o usuário
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_access_token = serializer.save()

        return Response( # Retorna o novo token de acesso
            {
                "message": "login was successfully",
                "new_access_token": new_access_token
            },
            status=status.HTTP_200_OK
        )        