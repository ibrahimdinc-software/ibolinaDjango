# Generated by Django 4.0.2 on 2022-03-27 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('binanceAPI', '0003_remove_positionmodel_isopen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='positionmodel',
            name='firstTPclosePrecentage',
            field=models.IntegerField(default=0, verbose_name='First TP Closing Percentage'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='positionmodel',
            name='firstTPrrRatio',
            field=models.FloatField(default=0, verbose_name='First TP Risk/Reward Ratio'),
            preserve_default=False,
        ),
    ]
