from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.shortcuts import redirect

from .models import User, AdminUser, Favorite, ReadingProgress, Bookmark
from .user_serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    FavoriteSerializer,
    ReadingProgressSerializer,
    BookmarkSerializer,
    AdminLoginSerializer,
    AdminUserSerializer,
    SendCodeSerializer,
)
from .oauth_utils import (
    get_qq_auth_url, get_qq_access_token, get_qq_openid, get_qq_userinfo,
)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except Exception as e:
                return Response({'detail': f'注册失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            from django.contrib.auth.backends import ModelBackend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_verification_code(self, request):
        """发送QQ邮箱验证码"""
        from .email_utils import send_verification_email
        from .models import EmailVerificationCode

        serializer = SendCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        # 生成验证码并保存到数据库
        try:
            record, code = EmailVerificationCode.generate_and_save(email)
        except Exception as e:
            return Response({'email': [f'验证码生成失败：{str(e)}']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 发送邮件
        try:
            send_verification_email(email, code)
        except ValueError as e:
            return Response({'email': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'email': [f'邮件发送失败：{str(e)}']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': '验证码已发送，请查收邮件'})

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': '登录成功',
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '退出登录成功'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'message': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        if not request.user.is_authenticated:
            return Response({'message': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        data = request.data

        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data:
            user.email = data['email']

        user.save()
        return Response({
            'message': '更新成功',
            'user': UserSerializer(user).data
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        if not request.user.is_authenticated:
            return Response({'message': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'old_password': ['请输入旧密码'], 'new_password': ['请输入新密码']}, status=400)

        if len(new_password) < 6:
            return Response({'new_password': ['密码至少6位']}, status=400)

        user = request.user
        if not user.check_password(old_password):
            return Response({'old_password': ['旧密码不正确']}, status=400)

        user.set_password(new_password)
        user.save()

        from django.contrib.auth import update_session_auth_hash
        update_session_authhash(request, user)

        return Response({'message': '密码修改成功'})

    @action(detail=False, methods=['post'])
    def admin_login(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.validated_data['admin']
            from django.utils import timezone
            from .auth import admin_login as do_admin_login
            admin.last_login = timezone.now()
            admin.save(update_fields=['last_login'])
            # 使用自定义认证后端写入 Session（关键修复）
            do_admin_login(request, admin)
            return Response({
                'message': '管理员登录成功',
                'user': {
                    'id': admin.id,
                    'username': admin.username,
                    'real_name': admin.real_name or '',
                    'is_staff': True,
                    'role': 'admin',
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def qq_login(self, request):
        """QQ OAuth登录"""
        code = request.query_params.get('code')
        state = request.query_params.get('state', '')

        if not code:
            auth_url = get_qq_auth_url(state=state)
            return Response({'auth_url': auth_url})

        try:
            token_data = get_qq_access_token(code)
            access_token = token_data.get('access_token', '')
            if not access_token:
                return Response({'error': 'QQ授权失败，未获取到access_token'}, status=status.HTTP_400_BAD_REQUEST)

            openid, unionid = get_qq_openid(access_token)
            if not openid:
                return Response({'error': 'QQ获取openid失败'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(qq_openid=openid).first()
            if user:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'message': 'QQ登录成功',
                    'token': token.key,
                    'user': UserSerializer(user).data
                })

            userinfo = get_qq_userinfo(access_token, openid)
            nickname = userinfo.get('nickname', '')
            avatar_url = userinfo.get('figureurl_qq_2') or userinfo.get('figureurl_qq_1') or ''
            username = nickname or f'qq_{openid[:8]}'

            user = User.objects.create(
                username=username,
                avatar=avatar_url,
                qq_openid=openid,
            )
            login(request, user)
            token = Token.objects.create(user=user)
            return Response({
                'message': 'QQ注册并登录成功',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'QQ登录异常: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def oauth_callback(self, request):
        """OAuth统一回调入口"""
        provider = request.query_params.get('provider', '')
        code = request.query_params.get('code', '')
        state = request.query_params.get('state', '')

        try:
            if provider == 'qq':
                if not code:
                    url = get_qq_auth_url(state=state)
                    return redirect(url)

                token_data = get_qq_access_token(code)
                access_token = token_data.get('access_token', '')
                if not access_token:
                    from urllib.parse import urlencode
                    return redirect(f'/login?{urlencode({"error": "QQ授权失败"})}')

                openid, _ = get_qq_openid(access_token)
                if not openid:
                    from urllib.parse import urlencode
                    return redirect(f'/login?{urlencode({"error": "QQ获取openid失败"})}')

                user = User.objects.filter(qq_openid=openid).first()
                if not user:
                    userinfo = get_qq_userinfo(access_token, openid)
                    nickname = userinfo.get('nickname', '')
                    avatar_url = userinfo.get('figureurl_qq_2') or userinfo.get('figureurl_qq_1') or ''
                    user = User.objects.create(
                        username=nickname or f'qq_{openid[:8]}',
                        avatar=avatar_url,
                        qq_openid=openid,
                    )

                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                from urllib.parse import urlencode
                return redirect(f'/login?{urlencode({"token": token.key})}')

            else:
                from urllib.parse import urlencode
                return redirect(f'/login?{urlencode({"error": "不支持的登录方式"})}')

        except Exception as e:
            from urllib.parse import urlencode
            return redirect(f'/login?{urlencode({"error": str(e)})}')


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .auth import AdminUser
        if isinstance(self.request.user, AdminUser):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        from .auth import AdminUser
        if isinstance(request.user, AdminUser):
            return Response({'message': '管理员无法收藏'}, status=status.HTTP_403_FORBIDDEN)
        novel_id = request.data.get('novel')
        if Favorite.objects.filter(user=request.user, novel_id=novel_id).exists():
            return Response({'message': '已收藏'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def check(self, request):
        from .auth import AdminUser
        if isinstance(request.user, AdminUser):
            return Response({'is_favorited': False})
        novel_id = request.query_params.get('novel_id')
        is_favorited = Favorite.objects.filter(user=request.user, novel_id=novel_id).exists()
        return Response({'is_favorited': is_favorited})

    @action(detail=False, methods=['post'])
    def delete_by_novel(self, request):
        from .auth import AdminUser
        if isinstance(request.user, AdminUser):
            return Response({'message': '管理员无收藏记录'}, status=status.HTTP_403_FORBIDDEN)
        novel_id = request.data.get('novel_id') or request.data.get('novel')
        if not novel_id:
            return Response({'message': '缺少书籍ID参数'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            favorite = Favorite.objects.get(user=request.user, novel_id=novel_id)
            favorite.delete()
            return Response({'message': '取消收藏成功'})
        except Favorite.DoesNotExist:
            return Response({'message': '收藏记录不存在'}, status=status.HTTP_404_NOT_FOUND)


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .auth import AdminUser
        if isinstance(self.request.user, AdminUser):
            return ReadingProgress.objects.none()
        return ReadingProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        from .auth import AdminUser
        if isinstance(self.request.user, AdminUser):
            return
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def get_progress(self, request):
        from .auth import AdminUser
        if isinstance(request.user, AdminUser):
            return Response({'message': '暂无阅读进度'})
        novel_id = request.query_params.get('novel_id')
        try:
            progress = ReadingProgress.objects.get(user=request.user, novel_id=novel_id)
            return Response(ReadingProgressSerializer(progress).data)
        except ReadingProgress.DoesNotExist:
            return Response({'message': '暂无阅读进度'})

    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        from .auth import AdminUser
        if isinstance(request.user, AdminUser):
            return Response({'message': '管理员无法更新阅读进度'}, status=status.HTTP_403_FORBIDDEN)
        novel_id = request.data.get('novel_id')
        chapter_id = request.data.get('chapter_id')
        position = request.data.get('position', 0)

        progress, created = ReadingProgress.objects.update_or_create(
            user=request.user,
            novel_id=novel_id,
            defaults={'chapter_id': chapter_id, 'position': position}
        )
        return Response({
            'message': '更新成功',
            'progress': ReadingProgressSerializer(progress).data
        })


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .auth import AdminUser
        if isinstance(self.request.user, AdminUser):
            return Bookmark.objects.none()
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        from .auth import AdminUser
        if isinstance(self.request.user, AdminUser):
            return
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_chapter(self, request):
        from .auth import AdminUser
        if isinstance(request.user, AdminUser):
            return Response({'message': '暂无书签'}, status=status.HTTP_404_NOT_FOUND)
        chapter_id = request.query_params.get('chapter_id')
        bookmark = Bookmark.objects.filter(user=request.user, chapter_id=chapter_id).first()
        if bookmark:
            return Response(BookmarkSerializer(bookmark).data)
        return Response({'message': '暂无书签'}, status=status.HTTP_404_NOT_FOUND)
