from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
import logging


logger = logging.getLogger('users')


class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        logger.info('Registration attempt for email: %s', email)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception('Registration failed for email: %s', email)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)