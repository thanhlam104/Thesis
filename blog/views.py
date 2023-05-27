from django.shortcuts import render
from .models import Post
# Create your views here.

def browse_posts(request):
    Data = {'posts': Post.objects.all().order_by('-date')}
    return render(request, 'blog/blog.html', Data)

def post(request, id):
    Data = {'post': Post.objects.get(id = id)}
    return render(request, 'blog/post.html', Data)