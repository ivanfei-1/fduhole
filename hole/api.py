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
import logging, base64, httpx
from datetime import datetime

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
                -1: 发送失败
                0 : 发送成功
                1: 用户名已注册
                2: 邮箱已注册
                3: 邮箱不在白名单内
            msg
    
    '''
    def get(self, request):

        username = request.query_params.get('username')
        email = request.query_params.get('email')

        # 检查用户名是否已注册
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
        # 获取数据
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # 检查用户名是否已注册
        if User.objects.filter(username=username):
            return Response({'data': 1, 'msg': '该用户名已注册！'})
        
        # 检查邮箱是否在白名单内
        domain = email[email.find('@')+1:]
        if not domain in settings.WHITELIST: return Response({'data': 3, 'msg': '邮箱不在白名单内！'})

        # 检查邮箱是否已注册
        for u in User.objects.all():
                if check_password(email, u.first_name):
                    return Response({'data': 2, 'msg': '该邮箱已注册！'})

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
    '''
    Returns: Discussion
        count: 0
        date_created: "1970-01-01T08:00:00.000000+08:00"
        date_updated: "2021-02-08T11:47:26.415943+08:00"
        first_post: Post
            content: "Lorem ipsum dolor sit amet ..."
            discussion: 42
            id: 1
            reply_to: null
            username: "bar"
        id: 25
        mapping: {foo: "bar"}
        tag: Array(3)
            0:
                color: "deep-orange"
                count: 1
                name: "tag1"
    '''
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        '''
        获取首页展示的discussions，按更新时间排序，分页
        url:  /api/discussions/
        Args:
            int: page
        Returns: 
            Discussion: Array(10)
        '''
        if 'pk' in kwargs:
            discussion = Discussion.objects.filter(pk=kwargs['pk'])
            if not discussion: return Response({'msg': '不存在'}, status=status.HTTP_404_NOT_FOUND)
            serializer = DiscussionSerializer(discussion[0])
            return Response(serializer.data)
        else: 
            if not request.query_params.get('page'): return Response({'msg': '需要提供page参数'}, status=status.HTTP_400_BAD_REQUEST)

            page = int(request.query_params.get('page'))
            interval = settings.INTERVAL

            discussions = Discussion.objects.order_by('-date_updated')[(page - 1) * interval : page * interval]

            serializer = DiscussionSerializer(discussions, many=True)
            return Response(serializer.data)

    def post(self, request):
        '''
        新增一个discussion。新增 discussion 的第一个 post 和若干 tag 并将其绑定到 discussion
        url:  /api/discussions/
        Args:
            content  不能全为空白
            tags     不能为空, 标签的数量不能超过 5 个, 标签名不能为空, 标签名不能超过8个字符, 标签颜色需在 Material Design 的主颜色列表内
        Returns:  
            Discussion
        '''
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
    '''
    Post:
        content: "Lorem ipsum dolor sit amet ..."
        date_created: "1970-01-01T08:00:00.000000+08:00"
        discussion: 42
        id: 1
        reply_to: null
        username: "foo"
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''
        获取某一discussion的posts
        url:  /api/posts/
        Args:  
            page 与 order 二者择一
            id      int     必须
            page    int     分页, 默认 10 个为间隔, 从 1 开始
            order   int     返回 order 楼层之后的所有帖子, order 从 1 开始
        Returns:
            Array of Posts
        '''
        discussion_id = int(request.query_params.get('id'))
        page = request.query_params.get('page')
        order = request.query_params.get('order')
        interval = settings.INTERVAL
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
        '''
        新增某一discussion下的post
        url:  /api/posts/
        Args:
            content         text    必须    内容
            discussion_id   int     必须    主题帖的主键
            post_id         int     可选    要回复的帖子的主键
        Returns:
            Post
        '''
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
        
        discussion.count = discussion.count + 1
        discussion.save()

        reply_to = None
        if post_id : reply_to = get_object_or_404(Post, pk=post_id)
        post = Post(username=username, content=content, discussion_id=discussion_id, reply_to=reply_to)
        post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data)

class TagsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        获取全部的 tags
        URL: /api/tags/
        Args: 无
        '''
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
