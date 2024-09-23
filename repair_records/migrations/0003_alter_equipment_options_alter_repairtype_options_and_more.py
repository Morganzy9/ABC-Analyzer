# Generated by Django 4.2.6 on 2023-11-14 09:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repair_records", "0002_alter_repairrecord_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="equipment",
            options={"verbose_name": "Жихоз", "verbose_name_plural": "Жихозлар"},
        ),
        migrations.AlterModelOptions(
            name="repairtype",
            options={
                "verbose_name": "Таъмир тури",
                "verbose_name_plural": "Таъмир турлари",
            },
        ),
        migrations.AlterField(
            model_name="repairtype",
            name="codename",
            field=models.CharField(max_length=5, verbose_name="Код"),
        ),
    ]