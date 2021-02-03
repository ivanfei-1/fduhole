from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest, JsonResponse
from django.conf import settings

from .utils import *
from .models import *
import logging

def register(request, message=''):
    if request.method == 'GET':
        return render(request, 'hole/register.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # check password
        if not password == password2:
            message = '两次输入的密码不符，请重试！'
            return render(request, 'hole/register.html', {'message': message})

        # check email domain
        domain = email[email.find('@')+1:]
        if not domain in settings.WHITELIST:
            message = '请使用edu邮箱注册！'
            return render(request, 'hole/register.html', {'message': message})

        # check if username exists
        if User.objects.filter(username=username):
            message = '该用户名已注册！'
            return render(request, 'hole/register.html', {'message': message})

        # check if email exists
        flag = False
        for u in User.objects.all():
            flag = flag or check_password(email, u.first_name)
        if flag == True:
            message = '该邮箱已注册！'
            return render(request, 'hole/register.html', {'message': message})

        # send verification email
        code = make_password(username)
        temp = TempUser(username=username, password=password, email=email, code=code)
        temp.save()
        mail(recipient=email, code=code, mode='register')
        return HttpResponse("验证邮件已发送，请点击邮件中的链接以继续")
        
def verify(request, code=None):
    if code:
        temp_user_set = TempUser.objects.filter(code=code)
        if temp_user_set:
            temp_user = temp_user_set[0]
            username = temp_user.username
            email = temp_user.email
            password = temp_user.password

            email = make_password(email)

            user = User.objects.create_user(username=username, password=password, first_name=email)
            user.groups.add(1)
            user.save()
            temp_user.delete()

            auth.login(request, user)
            return redirect('hole:index')
    
    return HttpResponseBadRequest('')

def login(request):
    if request.method == 'GET':
        return render(request, 'hole/login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('hole:index')
        else:
            return HttpResponse('用户名或密码错误！')

def logout(request):
    auth.logout(request)
    return redirect('hole:index')

@login_required
def index(request, page=1):
    if page <= 0: return HttpResponseBadRequest()
    interval = settings.INTERVAL
    count = Discussion.objects.count()
    discussions = Discussion.objects.order_by('-date_updated')[(page - 1) * interval : page * interval]
    previous_page, next_page = None, None
    if page > 1: previous_page = page - 1
    if count > page * interval : next_page = page + 1
    if not discussions: return Http404
    return render(request, 'hole/index.html', {'discussions': discussions, 'previous_page': previous_page,'next_page': next_page})

@login_required
def discussion(request, discussion_id, page=1):
    if page <= 0: return HttpResponseBadRequest()
    interval = settings.INTERVAL
    d = get_object_or_404(Discussion, pk=discussion_id)
    count = d.count
    posts = d.post_set.order_by('date_created')[(page - 1) * interval : page * interval]
    previous_page, next_page = None, None
    if page > 1: previous_page = page - 1
    if count > page * interval: next_page = page + 1
    count = (page - 1) * 10
    if not posts: return Http404
    return render(request, 'hole/discussion.html', {'posts': posts, 'discussion': d, 'previous_page': previous_page,'next_page': next_page, 'count': count})

@login_required
def create_post(request, discussion_id, post_id=None):
    if request.method == 'GET':
        reply_to = None
        if post_id : reply_to = get_object_or_404(Post, pk=post_id)
        else: pass
        return render(request, 'hole/create_post.html',{reply_to: reply_to})
 
    if request.method == 'POST':
        content = request.POST.get('content')
        discussion = get_object_or_404(Discussion, pk=discussion_id)
        mapping = discussion.mapping
        realname = request.user.username
        username = ''
        if realname in mapping:
            username = mapping[realname]
        else:
            while True:
                rname = random_name()
                if rname in mapping.values():
                    continue
                else:
                    username = rname
                    mapping[realname] = rname
                    break
        discussion.count = discussion.count + 1
        discussion.save()
        reply_to = None
        if post_id : reply_to = get_object_or_404(Post, pk=post_id)
        else: pass
        post = Post(username=username, content=content, discussion_id=discussion_id, reply_to=reply_to)
        post.save()
        return redirect('hole:discussion', discussion_id=discussion_id)

@login_required
def create_discussion(request):
    if request.method == 'GET':
        return render(request, 'hole/create_discussion.html')
    if request.method == 'POST':
        # tag =
        discussion = Discussion(count=0, mapping={})
        discussion.save()
        # create a post
        content = request.POST.get('content')
        anony_name = random_name()
        post = Post(username=anony_name, content=content, discussion_id=discussion.pk)
        post.save()
        # save the discussion
        discussion.mapping = {request.user.username : anony_name}
        discussion.first_post = post
        discussion.save()
        return redirect('hole:index')
