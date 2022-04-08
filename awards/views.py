from django.shortcuts import render,redirect, get_object_or_404
from django.http  import HttpResponse,Http404
import datetime as dt
from . forms import Registration,UpdateUser,UpdateProfile,postProjectForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.conf import settings
from .models import Profile,Post
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
import os

# Create your views here.
def home(request):
    projects = Post.display_posts()
    return render(request, 'home.html',{"posts": projects})

def register(request):
  if request.method == 'POST':
    form = Registration(request.POST)
    if form.is_valid():
      form.save()
      email = form.cleaned_data['email']
      username = form.cleaned_data.get('username')

      messages.success(request,f'Account for {username} created,you can now login')
      return redirect('registration/login.html')
  else:
    form = Registration()
  return render(request,'registration/registration_form.html',{"form":form})

@login_required
def post(request):
  if request.method == 'POST':
    post_form = postProjectForm(request.POST,request.FILES) 
    if post_form.is_valid():
      the_post = post_form.save(commit = False)
      the_post.user = request.user
      the_post.save()
      return redirect('home')

  else:
    post_form = postProjectForm()
  return render(request,'post.html',{"post_form":post_form})

@login_required
def profile(request):
  current_user = request.user
  posts = Post.objects.all()
  user_photos = Post.objects.filter(id = current_user.id).all()
  
  return render(request,'profile/profile.html',{"posts":posts,'user_photos':user_photos,"current_user":current_user})

def new_post(request):
    current_user = request.user
    if request.method == 'POST':
        form = postProjectForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = current_user
            article.save()
        return redirect('home')

    else:
        form = postProjectForm()
    return render(request, 'new_post.html', {"form": form})
  
def search_results(request):
    if 'post' in request.GET and request.GET["post"]:
        search_term = request.GET.get("post")
        projects = Post.search_by_title(search_term)
        message = f"{search_term}"

        return render(request, 'search.html',{"message":message,"projects": projects})

    else:
        message = "You haven't searched for any term"
        return render(request, 'search.html',{"message":message})

def users_profile(request,pk):
  user = User.objects.get(pk = pk)
  projects = Post.objects.filter(user = user)
  c_user = request.user
  
  return render(request,'profile/users_profile.html',{"user":user,"projects":projects,"c_user":c_user})

def update_profile(request):
  if request.method == 'POST':
    user_form = UpdateUser(request.POST,instance=request.user)
    profile_form = UpdateProfile(request.POST,request.FILES,instance=request.user.profile)
    if user_form.is_valid() and profile_form.is_valid():
      user_form.save()
      profile_form.save()
      messages.success(request,'Your Profile account has been updated successfully')
      return redirect('profile')
  else:
    user_form = UpdateUser(instance=request.user)
    profile_form = UpdateProfile(instance=request.user.profile) 
  params = {
    'user_form':user_form,
    'profile_form':profile_form
  }
  return render(request,'profile/update.html',params)


def detail(request,post_id):
  current_user = request.user
  try:
    post = get_object_or_404(Post, pk = post_id)
  except ObjectDoesNotExist:
    raise Http404()
  return render(request, 'post_detail.html', {'post':post,'current_user':current_user})