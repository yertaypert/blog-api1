from django.shortcuts import render
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
import logging


logger = logging.getLogger('users')


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='create')
class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    # @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        logger.info('Registration attempt for email: %s', email)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info('User registered: %s', user.email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
def ratelimit_response(request, exception):
    return Response(
        {"detail": "Too many requests. Try again later."},
        status=429
    )