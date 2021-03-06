# Generated by Django 4.0.3 on 2022-05-11 18:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0012_subjects_oe_course_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjects_oe',
            name='semester_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='student_management_app.semester'),
        ),
        migrations.AddField(
            model_name='subjects_oe',
            name='staff_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
