from django.shortcuts import  get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token

from .utils import *
from .models import *
from .serializer import *
import logging, base64, httpx, random
from datetime import datetime

class RegisterView(APIView):
    '''
    URL: register/

    '''

    def get(self, request):
        
        username = request.query_params.get('username')
        email = request.query_params.get('email')

        if username and email:
            # 检查用户名是否已注册
            if User.objects.filter(username=username):
                return Response({'data': 1, 'msg': '该用户名已注册！'})

            # 检查邮箱是否在白名单内
            domain = email[email.find('@')+1:]
            if not domain in settings.WHITELIST: return Response({'data': 3, 'msg': '邮箱不在白名单内！'})

            # 检查邮箱是否已注册
            # for u in User.objects.all():
            #     if check_password(email, u.first_name):
            #         return Response({'data': 2, 'msg': '该邮箱已注册！'})

            code = random.randint(100000, 999999)
            cache.set(username, code, 300)
            return Response(mail(recipient=email, code=code, mode='register'))

        if username:
            # 检查用户名是否已注册
            if User.objects.filter(username=username):
                return Response({'data': 1, 'msg': '该用户名已注册！'})
            else: return Response({'data': 0, 'msg': '该用户名未注册！'})

        if email:
            # 检查邮箱是否在白名单内
            # logging.error('开始检查邮箱')
            domain = email[email.find('@')+1:]
            if not domain in settings.WHITELIST: return Response({'data': 3, 'msg': '邮箱不在白名单内！'})
            # 检查邮箱是否已注册
            # for u in User.objects.all():
            #     logging.error(u.username)
            #     if check_password(email, u.first_name):
            #         return Response({'data': 2, 'msg': '该邮箱已注册！'})
            return Response({'data': 0, 'msg': '该邮箱未注册！'})

       
    def post(self, request):
        # 获取数据
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        code = request.data.get('code')
        api_key = request.data.get('api-key')

        if api_key:
            if not api_key in settings.API_KEY: 
                return Response({}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 检查邮箱是否在白名单内
            domain = email[email.find('@')+1:]
            if not domain in settings.WHITELIST: return Response({'data': 3, 'msg': '邮箱不在白名单内！'})

            # 用户名
            username = email[:email.find('@')]
            
            if not User.objects.filter(username=username): # 若未注册，创建用户
                email = make_password(email)
                user = User.objects.create_user(username=username, password=password, first_name=email)
                user.groups.add(1)
                user.save()
                Token.objects.create(user=user)

            request = httpx.post(
                'https://www.fduhole.tk/api/login/', 
                data={
                    'username': username,
                    'password': password,
                })
            request_code = request.status_code
            if request_code == 200:
                return Response(request.json())
            else:
                return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if code:
            # 检查用户名是否已注册
            if User.objects.filter(username=username):
                return Response({'data': 1, 'msg': '该用户名已注册！'})
            
            # 检查邮箱是否在白名单内
            domain = email[email.find('@')+1:]
            if not domain in settings.WHITELIST: return Response({'data': 3, 'msg': '邮箱不在白名单内！'})

            # 检查邮箱是否已注册
            # for u in User.objects.all():
            #         if check_password(email, u.first_name):
            #             return Response({'data': 2, 'msg': '该邮箱已注册！'})
            
            # 检查验证码
            try:
                code = int(code)
            except:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            if not cache.get(username) == code: return Response({'data': 4, 'msg': '验证码错误'}, status=status.HTTP_401_UNAUTHORIZED)

            email = make_password(email)

            user = User.objects.create_user(username=username, password=password, first_name=email)
            user.groups.add(1)
            user.save()

            Token.objects.create(user=user)

            return Response({'data': 0, 'msg': '注册成功, 跳转至登录页面'})

        return Response({}, status=status.HTTP_400_BAD_REQUEST)
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

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        discussion_id = request.query_params.get('discussion_id')
        tag_name = request.query_params.get('tag_name')
        page = request.query_params.get('page')
        order = request.query_params.get('order')

        if discussion_id:
            discussion = get_object_or_404(Discussion, pk=discussion_id)
            serializer = DiscussionSerializer(discussion)
            return Response(serializer.data)

        elif tag_name: # 默认按更新时间排序
            if order == 'last_created':
                discussions = get_object_or_404(Tag, name=tag_name).discussion_set.order_by('-date_created')
            else:
                discussions = get_object_or_404(Tag, name=tag_name).discussion_set.order_by('-date_updated')
            
        else: 
            if not page: return Response({'msg': '需要提供page参数'}, status=status.HTTP_400_BAD_REQUEST)
            page = int(page)
            interval = settings.INTERVAL
            if order == 'last_created':
                discussions = Discussion.objects.order_by('-date_created')[(page - 1) * interval : page * interval]
            else:
                discussions = Discussion.objects.order_by('-date_updated')[(page - 1) * interval : page * interval]

        serializer = DiscussionSerializer(discussions, many=True)
        return Response(serializer.data)

    def post(self, request):

        # 数据校验
        content = request.data.get('content')
        if not content.strip(): return Response({'msg': '内容不能为空！'}, status=status.HTTP_400_BAD_REQUEST)

        tags = request.data.get('tags')
        if len(tags) == 0: return Response({'msg': '标签不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if len(tags) >  5: return Response({'msg': '标签不能多于5个'}, status=status.HTTP_400_BAD_REQUEST)
        for tag in tags:
            if len(tag['name'].strip()) >  8: return Response({'msg': '标签名不能超过8个字符'}, status=status.HTTP_400_BAD_REQUEST)
            if not tag['name'].strip(): return Response({'msg': '标签名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            if not tag['color'] in settings.COLORLIST: return Response({'msg': '标签颜色不符合规范'}, status=status.HTTP_400_BAD_REQUEST)
    
        # 创建discussion， 创建tag并添加至discussion
        discussion = Discussion(count=0, mapping={})
        discussion.save()
        
        # 增/改 tags 并绑定至 discussion
        for tag in tags:
            new_tag = Tag.objects.filter(name=tag['name'])
            if new_tag:
                new_tag = new_tag[0]
                new_tag.count = new_tag.count + 1
                new_tag.save()
            else:
                new_tag = Tag(name=tag['name'], count=1, color=tag['color'])  # tag 的颜色为随机的 material design 标准主色   eg.'red'
                new_tag.save()

            discussion.tag.add(new_tag)

        # create a post
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

    def get(self, request, *args, **kwargs):
        post_id = request.query_params.get('post_id')
        discussion_id = request.query_params.get('id')
        page = request.query_params.get('page')
        order = request.query_params.get('order')
        search = request.query_params.get('search')
        interval = settings.INTERVAL

        if post_id:
            post_id = int(post_id)
            post = get_object_or_404(Post, pk=post_id)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        elif search:
            posts = Post.objects.filter(content__icontains=search).order_by('-date_created')
        else:
            discussion_id = int(discussion_id)
            d = get_object_or_404(Discussion, pk=discussion_id)
    
            if order: 
                order = int(order)
                posts = d.post_set.order_by('date_created')[order:]
                
            if page:
                page = int(page)
                posts = d.post_set.order_by('date_created')[(page - 1) * interval : page * interval]

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):

        content = request.data.get('content')
        discussion_id = request.data.get('discussion_id')
        post_id = request.data.get('post_id')
        
        if not content: return Response({'msg': '内容不能为空！'}, status=status.HTTP_400_BAD_REQUEST)
        if not discussion_id: return Response({'msg': 'discussion id 不能为空！'}, status=status.HTTP_400_BAD_REQUEST)

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

        reply_to = None
        if post_id : reply_to = post_id
        post = Post(username=username, content=content, discussion_id=discussion_id, reply_to=reply_to)
        post.save()
        
        discussion.count = discussion.count + 1
        discussion.save()

        serializer = PostSerializer(post)
        return Response(serializer.data)

class TagsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # name = request.query_params.get('name')
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

class ImagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        img = request.data.get('img')
        if not img: return Response({'msg': '内容不能为空！'}, status=status.HTTP_400_BAD_REQUEST)

        base64_data = base64.b64encode(img.read())  # base64编码
        img_str = str(base64_data, 'utf-8')

        datetime_str = str(datetime.now())
        date = datetime_str[:10]
        time = datetime_str[11:]
        mime = img.name.split('.')[-1]
        url = 'https://api.github.com/repos/fduhole/web/contents/{date}/{time}.{mime}'.format(date=date, time=time, mime=mime)

        headers = {
            'Authorization': 'token {}'.format(settings.GITHUB_TOKEN)
        }

        body = {
            'content': img_str,
            'message': 'upload image by user {}'.format(request.user.username),
            'branch': 'img'
        }

        r = httpx.put(url, headers=headers, json=body)

        if r.status_code == 201:
            url = 'https://cdn.jsdelivr.net/gh/fduhole/web@img/{date}/{time}.{mime}'.format(date=date, time=time, mime=mime)
            return Response({'url': url, 'msg': '图片上传成功!'})
        else:
            return Response(r.json(), status=status.HTTP_400_BAD_REQUEST)
