# Generated by Django 4.0.6 on 2022-10-22 02:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aadiscordbot', '0008_channels_deleted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quotemessage',
            options={'default_permissions': (), 'permissions': (('quote_save', 'Can save quotes'),),
                     'verbose_name': 'Quote Message', 'verbose_name_plural': 'Quote Messages'},
        ),
    ]
