# Generated by Django 4.2.6 on 2024-03-22 05:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repair_records', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workaction',
            name='description',
        ),
    ]