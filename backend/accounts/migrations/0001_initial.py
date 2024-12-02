# Generated by Django 5.1.3 on 2024-11-15 12:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('M', '남성'), ('F', '여성'), ('O', '기타')], max_length=1)),
                ('age_group', models.CharField(choices=[('10', '10대'), ('20', '20대'), ('30', '30대'), ('40', '40대'), ('50', '50대 이상')], max_length=2)),
                ('income_level', models.CharField(choices=[('L', '저소득'), ('M', '중소득'), ('H', '고소득')], max_length=1)),
                ('dummy_field', models.BooleanField(default=True)),
                ('preferred_categories', models.ManyToManyField(blank=True, to='products.productcategory')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
