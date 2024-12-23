# Generated by Django 4.2.6 on 2024-02-05 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repair_records', '0015_alter_equipment_break_affect_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentInactiveTime',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('datetime', models.DateTimeField(verbose_name='Start/End time fo Inactivity')),
                ('active_type', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], max_length=1, verbose_name='Activity Type')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repair_records.equipment')),
            ],
            options={
                'verbose_name': 'Equipment Inactive Time',
                'verbose_name_plural': 'Equipment Inactive Times',
            },
        ),
    ]
