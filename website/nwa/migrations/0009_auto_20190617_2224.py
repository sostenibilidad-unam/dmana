# Generated by Django 2.2 on 2019-06-17 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nwa', '0008_auto_20190617_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='nwa.Organization'),
        ),
        migrations.AlterField(
            model_name='person',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='nwa.Sector'),
        ),
    ]
