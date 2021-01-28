from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest


from .utils import mail, ranstr
from .models import *
import logging
# Create your views here.
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
        whitelist = ['fudan.edu.cn']
        if not domain in whitelist:
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
def index(request):
    discussions = []
    post_pk = []
    query = Discussion.objects.order_by('-date_updated')[:10]
    for d in query:
        discussions.append(d)
        post_pk.append(d.first_post)
    posts = Post.objects.filter(pk__in=post_pk)
    data = zip(discussions, posts)
    return render(request, 'hole/index.html', {'data': data})

@login_required
def discussion(request, pk):
    d = Discussion.objects.get(pk=pk)
    posts = d.post_set.order_by('date_created')[:10]
    return render(request, 'hole/discussion.html', {'posts': posts, 'discussion': d})