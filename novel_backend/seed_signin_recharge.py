import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import SigninReward, RechargePlan

# 签到奖励配置（1-7天连续签到）
rewards = [
    {'day': 1, 'coins': 10},
    {'day': 2, 'coins': 15},
    {'day': 3, 'coins': 20},
    {'day': 4, 'coins': 25},
    {'day': 5, 'coins': 30},
    {'day': 6, 'coins': 40},
    {'day': 7, 'coins': 50},   # 周签到大奖
    {'day': 14, 'coins': 80},
    {'day': 21, 'coins': 120},
    {'day': 30, 'coins': 200}, # 月签超级大奖
]
for r in rewards:
    SigninReward.objects.update_or_create(day=r['day'], defaults={'coins': r['coins']})
print(f'Signin rewards: {len(rewards)} configs seeded')

# 充值套餐
plans = [
    {'name': '月卡会员', 'plan_type': 'monthly', 'price': 19.9, 'days': 30,
     'description': '全站免广告+专属标识，畅享阅读'},
    {'name': '季卡会员', 'plan_type': 'quarterly', 'price': 49.9, 'days': 90,
     'description': '省20元！免广告3个月，超值之选'},
    {'name': '年卡会员', 'plan_type': 'yearly', 'price': 168.0, 'days': 365,
     'description': '省70元！全年免广告，尊享特权'},
]
for p in plans:
    RechargePlan.objects.update_or_create(
        plan_type=p['plan_type'],
        defaults={
            'name': p['name'],
            'price': p['price'],
            'days': p['days'],
            'description': p['description'],
            'sort_order': ['monthly','quarterly','yearly'].index(p['plan_type']),
        }
    )
print(f'Recharge plans: {len(plans)} plans seeded')

# 验证
print(f'\nSigninReward count: {SigninReward.objects.count()}')
for s in SigninReward.objects.all():
    print(f'  Day {s.day}: +{s.coins} coins')
print(f'\nRechargePlan count: {RechargePlan.objects.count()}')
for p in RechargePlan.objects.all():
    print(f'  {p.name}: ¥{p.price} / {p.days} days')
