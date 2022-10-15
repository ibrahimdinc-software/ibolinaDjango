# Generated by Django 4.0.2 on 2022-03-31 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('binanceAPI', '0014_alter_positionmodel_trailingclose'),
    ]

    operations = [
        migrations.AddField(
            model_name='pairmodel',
            name='trailingClose',
            field=models.BooleanField(default=True, verbose_name='Use Trailing Close'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='positionmodel',
            name='trailingClose',
            field=models.BooleanField(verbose_name='Use Trailing Close'),
        ),
    ]