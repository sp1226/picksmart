# Generated by Django 5.1.3 on 2024-11-17 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbehavior',
            name='view_duration',
            field=models.FloatField(default=0),
        ),
    ]