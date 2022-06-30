# Generated by Django 4.0.3 on 2022-06-27 07:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0024_remove_forms_oe_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forms_oe',
            name='semester_name',
        ),
        migrations.AddField(
            model_name='forms_oe',
            name='username',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]