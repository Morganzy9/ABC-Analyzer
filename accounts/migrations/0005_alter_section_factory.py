# Generated by Django 4.2.6 on 2023-12-14 04:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_section_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='factory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.factory', verbose_name='Factory'),
        ),
    ]
