# Generated by Django 4.0.6 on 2022-09-17 11:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aadiscordbot', '0006_goodbyemessage_welcomemessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteMessage',
            fields=[
                ('message', models.BigIntegerField(
                    primary_key=True, serialize=False)),
                ('content', models.CharField(max_length=1000)),
                ('datetime', models.DateTimeField(blank=True, null=True)),
                ('author', models.PositiveBigIntegerField()),
                ('author_nick', models.CharField(
                    blank=True, max_length=50, null=True)),
                ('reference', models.CharField(
                    help_text='Nickname for this quote', max_length=100)),
                ('channel', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='aadiscordbot.channels')),
                ('server', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='aadiscordbot.servers')),
            ],
        ),
    ]
