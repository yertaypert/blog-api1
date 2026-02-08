from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def hello(request):
    return HttpResponse("Hello")


def my_view(request):

    if request.method == 'GET':
        name = request.GET.get('name', 'world')
        message = f"Hello, {name}! This is a simple GET request example."
        return HttpResponse(message)
    else:
        return HttpResponse("Method not allowed", status=405)