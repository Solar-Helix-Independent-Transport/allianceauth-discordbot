# Generated by Django 4.0.10 on 2023-06-30 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('aadiscordbot', '0009_alter_quotemessage_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='discordbot',
            options={'default_permissions': (), 'managed': False, 'permissions': (
                ('basic_access', 'Can access this app.'), ('member_command_access', 'can access the member commands.'))},
        ),
        migrations.CreateModel(
            name='TicketGroups',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('groups', models.ManyToManyField(blank=True,
                 help_text='Pingable groups for ticketing', to='auth.group')),
            ],
            options={
                'default_permissions': (),
            },
        ),
    ]
