# Generated by Django 4.0.2 on 2022-03-27 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('binanceAPI', '0002_positionmodel_isopen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='positionmodel',
            name='isOpen',
        ),
        migrations.RemoveField(
            model_name='positionmodel',
            name='side',
        ),
        migrations.AddField(
            model_name='positionmodel',
            name='bigDonLen',
            field=models.IntegerField(default='0', verbose_name='Big Don Len'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='positionmodel',
            name='emaLen',
            field=models.IntegerField(default='0', verbose_name='EMA Len'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='positionmodel',
            name='rrRatio',
            field=models.FloatField(default=0.6, verbose_name='Risk/Reward Ratio'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='positionmodel',
            name='smallDonLen',
            field=models.IntegerField(default=0, verbose_name='Small Don Len'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='positionmodel',
            name='trailingClose',
            field=models.BooleanField(default=True, verbose_name='Use Trailing Close'),
            preserve_default=False,
        ),
    ]
