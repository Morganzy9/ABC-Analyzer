# Generated by Django 4.2.6 on 2023-11-23 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repair_records', '0008_alter_equipment_options_alter_repairrecord_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repairrecord',
            name='end_time',
            field=models.DateTimeField(verbose_name='End Time'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='start_time',
            field=models.DateTimeField(verbose_name='Start Time'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='total_time',
            field=models.DurationField(blank=True, null=True, verbose_name='Total Time'),
        ),
    ]