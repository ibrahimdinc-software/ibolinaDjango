# Generated by Django 4.0.2 on 2022-04-03 23:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('binanceAPI', '0023_alter_pairmodel_cooldowndate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pairmodel',
            old_name='coolDownDate',
            new_name='cooldownDate',
        ),
    ]
