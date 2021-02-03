from django.shortcuts import  get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token

from .utils import *
from .models import *
from .serializer import *

class RegisterView(APIView):
    '''
    url: register/

    GET: 检查用户名是否未注册，检查邮箱是否在白名单内且未注册，返回检查是否通过的bool值
        Args:
            username 或 email (不能同时提供两者)
        Returns:
            data: 
                0: 验证通过
                1: 用户名已注册
                2: 邮箱已注册
                3: 邮箱不在白名单内
            msg

    POST: 发送验证邮件
        Args: 
            username
            password
            email
        Returns: 
            data: 
                0 : 发送成功
                -1: 发送失败
            msg
    
    '''
    def get(self, request):

        username = request.query_params.get('username')
        email = request.query_params.get('email')

        if username:
            if User.objects.filter(username=username):
                return Response({'data': 1, 'msg': '该用户名已注册！'})
            else: return Response({'data': 0, 'msg': '该用户名未注册！'})

        if email:
            # 检查邮箱是否在白名单内
            domain = email[email.find('@')+1:]
            if not domain in settings.WHITELIST: return Response({'data': 3, 'msg': '邮箱不在白名单内！'})
            # 检查邮箱是否已注册
            for u in User.objects.all():
                if check_password(email, u.first_name):
                    return Response({'data': 2, 'msg': '该邮箱已注册！'})
            return Response({'data': 0, 'msg': '该邮箱未注册！'})

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        code = make_password(username)
        temp = TempUser(username=username, password=password, email=email, code=code)
        temp.save()

        return Response(mail(recipient=email, code=code, mode='register'))

class VerifyView(APIView):
    '''
    URL: verify/

    GET: 接收验证链接并正式创建用户
        Args: code
        Returns: user data
    '''
    def get(self, request):
        code = request.query_params.get('code')
        code = code.replace(' ', '+')           # 防止 url 自动将加号转义

        if not code: return Response(status=status.HTTP_400_BAD_REQUEST)

        temp_user_set = TempUser.objects.filter(code=code)
        if not temp_user_set: return Response(status=status.HTTP_404_NOT_FOUND)

        temp_user = temp_user_set[0]
        username = temp_user.username
        email = temp_user.email
        password = temp_user.password

        email = make_password(email)

        user = User.objects.create_user(username=username, password=password, first_name=email)
        user.groups.add(1)
        user.save()
        temp_user.delete()

        Token.objects.create(user=user)

        return HttpResponse("用户 %s 注册成功，请返回登录页面登录！" % username)

class LoginView(APIView):
    '''
    POST: 登录
        Args:
            username
            password
            
    GET: 登出
        Args: 
    '''
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return Response({'msg': '%s 登录成功！' % username})
        else:
            return Response({'msg': '用户名或密码错误！'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def get(self, request):
            username = request.user.username
            auth.logout(request)
            return Response({'msg': '%s 已登出！' % username})

class DiscussionsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        获取首页展示的discussions，按更新时间排序，分页
        url:  /hole/discussions/
        Args:
            int: page
        '''
        page = int(request.query_params.get('page'))
        interval = settings.INTERVAL
        count = Discussion.objects.count()
        discussions = Discussion.objects.order_by('-date_updated')[(page - 1) * interval : page * interval]

        serializer = DiscussionSerializer(discussions, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        新增一个discussion，创建一个discussion对象和它的第一个post对象
        url:  /hole/discussions/
        Args:
            text: content 
        Returns:
            该discussion
        '''
         # tag =
        discussion = Discussion(count=0, mapping={})
        discussion.save()

        # create a post
        content = request.data.get('content')
        anony_name = random_name()
        post = Post(username=anony_name, content=content, discussion_id=discussion.pk)
        post.save()

        # save the discussion
        discussion.mapping = {request.user.username : anony_name}
        discussion.first_post = post
        discussion.save()

        serializer = DiscussionSerializer(discussion)
        return Response(serializer.data)

class PostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        获取某一discussion的posts，用于discussion页面，分页
        url:  /hole/posts/
        Args:
            int: discussion_id
            int: page
        '''
        discussion_id = int(request.query_params.get('id'))
        page = int(request.query_params.get('page'))
        interval = settings.INTERVAL
        d = get_object_or_404(Discussion, pk=discussion_id)
        count = d.count
        posts = d.post_set.order_by('date_created')[(page - 1) * interval : page * interval]

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        新增某一discussion下的post
        url:  /hole/posts/
        Args:
            text: content 
            int : discussion_id
            int : post_id (可选，回复一条post的主键)
        Returns:
            该post
        '''
        content = request.data.get('content')
        discussion_id = request.data.get('discussion_id')
        post_id = request.data.get('post_id')
        
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
        post = Post(username=username, content=content, discussion_id=discussion_id, reply_to=reply_to)
        post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data)