# Generated by Django 4.2.6 on 2023-11-16 21:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "repair_records",
            "0005_rename_breaking_affect_equipment_break_affect_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="repairrecord",
            name="total_time",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, verbose_name="Умумий вакт"
            ),
        ),
    ]
