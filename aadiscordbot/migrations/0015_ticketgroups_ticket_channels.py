# Generated by Django 4.2.16 on 2024-10-11 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aadiscordbot', '0014_alter_goodbyemessage_guild_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketgroups',
            name='ticket_channels',
            field=models.TextField(blank=True, default=None, help_text='JSON dictionary {server_id:channel_id}', null=True),
        ),
    ]
