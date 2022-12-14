# Generated by Django 4.0.4 on 2022-05-15 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('binanceAPI', '0026_remove_pairmodel_firsttpprice_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='klineindicatormodel',
            name='bigDonLB',
        ),
        migrations.RemoveField(
            model_name='klineindicatormodel',
            name='bigDonUB',
        ),
        migrations.RemoveField(
            model_name='klineindicatormodel',
            name='ema',
        ),
        migrations.RemoveField(
            model_name='klineindicatormodel',
            name='smallDonLB',
        ),
        migrations.RemoveField(
            model_name='klineindicatormodel',
            name='smallDonUB',
        ),
        migrations.RemoveField(
            model_name='pairmodel',
            name='bigDonLen',
        ),
        migrations.RemoveField(
            model_name='pairmodel',
            name='smallDonLen',
        ),
        migrations.AddField(
            model_name='klineindicatormodel',
            name='hma',
            field=models.FloatField(default=0, verbose_name='HullMA'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='klineindicatormodel',
            name='pmax',
            field=models.FloatField(default=0, verbose_name='PMax'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='klineindicatormodel',
            name='var',
            field=models.FloatField(default=0, verbose_name='VAR'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pairmodel',
            name='hmaLen',
            field=models.IntegerField(default=0, verbose_name='HullMA Length'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pairmodel',
            name='pMaxLen',
            field=models.IntegerField(default=0, verbose_name='PMax Length'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pairmodel',
            name='pMaxMultiplier',
            field=models.FloatField(default=0, verbose_name='PMax Multiplier Length'),
            preserve_default=False,
        ),
    ]
