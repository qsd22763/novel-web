from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date, timedelta

from .models import CheckIn, CheckInConfig, MembershipOrder, User
from .auth import AdminUser
from .user_serializers import CheckInSerializer, MembershipOrderSerializer


class CheckInViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def do_checkin(self, request):
        """每日签到"""
        user = request.user
        if isinstance(user, AdminUser):
            return Response({'message': '管理员无需签到'}, status=status.HTTP_403_FORBIDDEN)

        today = date.today()
        if CheckIn.objects.filter(user=user, check_date=today).exists():
            return Response({
                'message': '今日已签到',
                'checked_today': True,
            }, status=status.HTTP_400_BAD_REQUEST)

        config = CheckInConfig.get_config()
        reward = config.daily_reward

        # 创建签到记录
        record = CheckIn.objects.create(
            user=user,
            check_date=today,
            reward_coins=reward,
        )
        # 增加虚拟币
        user.coins = (user.coins or 0) + reward
        user.save(update_fields=['coins'])

        # 计算连续签到天数
        consecutive = self._calc_consecutive(user, today)

        return Response({
            'message': f'签到成功，获得 {reward} 虚拟币',
            'checked_today': True,
            'reward_coins': reward,
            'total_coins': user.coins,
            'consecutive_days': consecutive,
            'record': CheckInSerializer(record).data,
        })

    @action(detail=False, methods=['get'])
    def status(self, request):
        """签到状态：是否已签到、连续天数、虚拟币余额"""
        user = request.user
        if isinstance(user, AdminUser):
            return Response({
                'checked_today': False,
                'consecutive_days': 0,
                'total_coins': 0,
                'config': {'daily_reward': 10},
            })

        today = date.today()
        checked_today = CheckIn.objects.filter(user=user, check_date=today).exists()
        consecutive = self._calc_consecutive(user, today) if checked_today else self._calc_consecutive(user, today - timedelta(days=1))
        config = CheckInConfig.get_config()

        return Response({
            'checked_today': checked_today,
            'consecutive_days': consecutive,
            'total_coins': user.coins or 0,
            'is_vip': user.is_vip,
            'vip_expire_date': user.vip_expire_date.strftime('%Y-%m-%d %H:%M') if user.vip_expire_date else None,
            'config': {
                'daily_reward': config.daily_reward,
            },
        })

    @action(detail=False, methods=['get'])
    def records(self, request):
        """我的签到记录（近30天）"""
        user = request.user
        if isinstance(user, AdminUser):
            return Response({'results': [], 'count': 0})

        days = int(request.query_params.get('days', 30))
        start = date.today() - timedelta(days=days)
        records = CheckIn.objects.filter(
            user=user, check_date__gte=start
        ).order_by('-check_date')
        serializer = CheckInSerializer(records, many=True)
        return Response({
            'results': serializer.data,
            'count': records.count(),
        })

    def _calc_consecutive(self, user: User, from_date: date) -> int:
        """从指定日期向前计算连续签到天数"""
        consecutive = 0
        d = from_date
        while True:
            if CheckIn.objects.filter(user=user, check_date=d).exists():
                consecutive += 1
                d -= timedelta(days=1)
            else:
                break
            if consecutive > 365:
                break
        return consecutive


class MembershipViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    PLAN_CONFIG = {
        'monthly': {'name': '月卡', 'days': 30, 'price': 19.9},
        'quarterly': {'name': '季卡', 'days': 90, 'price': 49.9},
        'yearly': {'name': '年卡', 'days': 365, 'price': 168.0},
    }

    @action(detail=False, methods=['get'])
    def plans(self, request):
        """获取会员套餐列表"""
        return Response([
            {'key': k, **v} for k, v in self.PLAN_CONFIG.items()
        ])

    @action(detail=False, methods=['get'])
    def my_status(self, request):
        """当前会员状态"""
        user = request.user
        is_vip = False
        expire_str = None
        if isinstance(user, AdminUser):
            is_vip = True
        elif user.is_vip and user.vip_expire_date:
            if user.vip_expire_date > timezone.now():
                is_vip = True
                expire_str = user.vip_expire_date.strftime('%Y-%m-%d %H:%M')
            else:
                # 过期自动更新
                user.is_vip = False
                user.save(update_fields=['is_vip'])

        return Response({
            'is_vip': is_vip,
            'vip_expire_date': expire_str,
        })

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """创建充值订单（模拟支付）"""
        user = request.user
        if isinstance(user, AdminUser):
            return Response({'message': '管理员无需购买会员'}, status=status.HTTP_403_FORBIDDEN)

        plan_type = request.data.get('plan_type')
        if plan_type not in self.PLAN_CONFIG:
            return Response({'message': '无效的套餐类型'}, status=status.HTTP_400_BAD_REQUEST)

        plan = self.PLAN_CONFIG[plan_type]
        import uuid
        order_no = f'MX{timezone.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6].upper()}'

        now = timezone.now()
        expire_at = now + timedelta(days=plan['days'])

        order = MembershipOrder.objects.create(
            user=user,
            order_no=order_no,
            plan_type=plan_type,
            amount=plan['price'],
            status='paid',
            paid_at=now,
            expire_at=expire_at,
        )

        # 激活会员
        user.is_vip = True
        user.vip_expire_date = expire_at
        user.save(update_fields=['is_vip', 'vip_expire_date'])

        return Response({
            'message': f'{plan["name"]}开通成功',
            'order': MembershipOrderSerializer(order).data,
            'is_vip': True,
            'vip_expire_date': expire_at.strftime('%Y-%m-%d %H:%M'),
        })

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """我的订单列表"""
        user = request.user
        if isinstance(user, AdminUser):
            return Response({'results': [], 'count': 0})

        orders = MembershipOrder.objects.filter(user=user).order_by('-created_at')[:20]
        serializer = MembershipOrderSerializer(orders, many=True)
        return Response({
            'results': serializer.data,
            'count': orders.count(),
        })
