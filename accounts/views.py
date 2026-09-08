from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .serializers import RegisterAccountSerializer

class RegisterAccountView(APIView): # Registra um usuário
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = RegisterAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "account created successfully"}, status=status.HTTP_201_CREATED)