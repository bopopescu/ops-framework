# Generated by Django 2.1.7 on 2019-05-09 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0008_auto_20190509_1230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalnormalservice',
            name='git',
        ),
        migrations.RemoveField(
            model_name='normalservice',
            name='git',
        ),
    ]
