from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import RegisterAccountSerializer, LoginAccountSerializer, RefreshTokenSerializer, ResetPasswordRequestSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .services import revoke_account_refresh_tokens

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

class LogoutAccountView(APIView): # Realiza logout
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        revoke_account_refresh_tokens(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

class ResetPasswordRequestView(APIView): # Requisita reset de senha (para usuários logados)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = ResetPasswordRequestSerializer(data={}, context={"account":request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': "an email with a reset link was sent to you"}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView): # Requisita reset de senha (para usuários não logados)
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "an email with a reset link was sent to you"}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView): # View responsável por mudar a senha de uma conta
    permission_classes = [permissions.AllowAny]

    def post(self, request, reset_token, *args, **kwargs):

        if not reset_token:
            return Response({"detail": "reset_token is required as a query parameter"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data, context={"reset_token":reset_token})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "password updated successfully"}, status=status.HTTP_200_OK)