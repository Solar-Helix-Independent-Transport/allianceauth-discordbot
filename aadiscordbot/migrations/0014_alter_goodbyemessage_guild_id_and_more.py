# Generated by Django 5.0.3 on 2024-05-25 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aadiscordbot', '0013_goodbyemessage_guild_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodbyemessage',
            name='guild_id',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='welcomemessage',
            name='guild_id',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
    ]
