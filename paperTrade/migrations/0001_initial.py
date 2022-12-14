# Generated by Django 4.0.4 on 2022-05-15 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('binanceAPI', '0027_remove_klineindicatormodel_bigdonlb_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperAccountModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Account Name')),
                ('balance', models.FloatField(verbose_name='Balance')),
                ('leverage', models.IntegerField(verbose_name='Leverage')),
                ('percentage', models.FloatField(verbose_name='Percentage')),
                ('inPosition', models.BooleanField(verbose_name='In Postition')),
            ],
        ),
        migrations.CreateModel(
            name='PaperPositionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entryTime', models.DateTimeField(auto_now_add=True, verbose_name='Entry Time')),
                ('side', models.CharField(max_length=255, verbose_name='Position Side')),
                ('firstTpProfit', models.FloatField(blank=True, null=True, verbose_name='First TP Profit')),
                ('secondTpProfit', models.FloatField(blank=True, null=True, verbose_name='Second TP Profit')),
                ('lastTpProfit', models.FloatField(blank=True, null=True, verbose_name='Last TP Profit')),
                ('isActive', models.BooleanField(default=True, verbose_name='Is Active')),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='binanceAPI.pairmodel')),
                ('paperAccount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paperTrade.paperaccountmodel', verbose_name='Paper Account')),
            ],
        ),
        migrations.CreateModel(
            name='PaperPositionLogModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logDate', models.DateTimeField(auto_now_add=True, verbose_name='Log Date')),
                ('logType', models.CharField(choices=[('enter', 'Enter Pos'), ('first', 'First TP'), ('second', 'Second TP'), ('last', 'Last TP'), ('close', 'Close Pos'), ('stop', 'Stop Pos')], max_length=255, verbose_name='Log Type')),
                ('price', models.FloatField(verbose_name='Price')),
                ('paperPosition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paperTrade.paperpositionmodel', verbose_name='Paper Position')),
            ],
        ),
    ]
