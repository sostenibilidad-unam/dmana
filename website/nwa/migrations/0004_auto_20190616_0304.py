# Generated by Django 2.2.2 on 2019-06-16 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nwa', '0003_auto_20190616_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='action',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='organization',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='sector',
            name='sector',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]