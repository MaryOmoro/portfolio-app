from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse(request, 'base/home.html')

def posts(request):
    return HttpResponse(request, 'base/posts.html')

def post(request):
    return HttpResponse(request, 'base/post.html')

def profile(request):
    return HttpResponse(request, 'base/profile.html')
