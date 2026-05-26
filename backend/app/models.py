from django.db import models
from django.contrib.auth.models import User

# 分类
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

# 商品
class Goods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    desc = models.TextField()
    image = models.ImageField(upload_to='goods/')
    status = models.IntegerField(default=1)  # 1上架 0下架
    create_time = models.DateTimeField(auto_now_add=True)

# 购物车
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    num = models.IntegerField(default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user','goods')

# 订单
class Order(models.Model):
    order_no = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(default=0) # 0待支付 1已支付
    receiver = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)

# 订单项
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    num = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)