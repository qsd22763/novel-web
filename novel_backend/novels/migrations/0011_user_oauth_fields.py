# Generated for User OAuth fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0010_emailverificationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='qq_openid',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='QQ OpenID', db_index=True),
        ),
        migrations.AddField(
            model_name='user',
            name='wechat_openid',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='微信OpenID', db_index=True),
        ),
    ]
