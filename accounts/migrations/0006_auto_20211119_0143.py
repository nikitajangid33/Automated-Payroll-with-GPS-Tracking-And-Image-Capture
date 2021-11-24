# Generated by Django 3.2.7 on 2021-11-18 20:13

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0005_employee_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeworklocations',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='UserLoggedIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loggedIntime', models.DateTimeField(default=datetime.datetime.now)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
