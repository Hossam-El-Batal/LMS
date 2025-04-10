# Generated by Django 4.2.20 on 2025-04-01 15:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(max_length=13, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('publication_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('authors', models.ManyToManyField(related_name='books', to='authors.author')),
                ('categories', models.ManyToManyField(related_name='books', to='books.category')),
            ],
        ),
    ]
