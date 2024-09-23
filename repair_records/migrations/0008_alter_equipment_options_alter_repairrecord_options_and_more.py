# Generated by Django 4.2.6 on 2023-11-22 04:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0002_section'),
        ('repair_records', '0007_alter_repairrecord_total_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='equipment',
            options={'verbose_name': 'Equipment',
                     'verbose_name_plural': 'Equipments'},
        ),
        migrations.AlterModelOptions(
            name='repairrecord',
            options={'permissions': [('summarize_repairrecord', 'Can summarize repair record')],
                     'verbose_name': 'Repair Record', 'verbose_name_plural': 'Repair Records'},
        ),
        migrations.AlterModelOptions(
            name='repairtype',
            options={'verbose_name': 'Repair Type',
                     'verbose_name_plural': 'Repair Types'},
        ),
        migrations.AlterField(
            model_name='equipment',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='end_time',
            field=models.TimeField(verbose_name='End Time'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='repair_records.equipment', verbose_name='Equipment'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='factory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='accounts.factory', verbose_name='Factory'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING,
                                    to=settings.AUTH_USER_MODEL, verbose_name='Master'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='reason',
            field=models.TextField(verbose_name='Reason'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='repair_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='repair_records.repairtype', verbose_name='Repair Type'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='start_time',
            field=models.TimeField(verbose_name='Start Time'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='total_time',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Total Time'),
        ),
        migrations.AlterField(
            model_name='repairrecord',
            name='work_done',
            field=models.TextField(verbose_name='Work Done'),
        ),
        migrations.AlterField(
            model_name='repairtype',
            name='codename',
            field=models.CharField(max_length=5, verbose_name='CodeName'),
        ),
        migrations.AlterField(
            model_name='repairtype',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
    ]