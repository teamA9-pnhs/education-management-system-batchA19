# Generated by Django 4.0.3 on 2022-05-11 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0010_subjects_oe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subjects_oe',
            name='course_id',
        ),
        migrations.RemoveField(
            model_name='subjects_oe',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='subjects_oe',
            name='semester_id',
        ),
        migrations.RemoveField(
            model_name='subjects_oe',
            name='staff_id',
        ),
        migrations.RemoveField(
            model_name='subjects_oe',
            name='updated_at',
        ),
    ]