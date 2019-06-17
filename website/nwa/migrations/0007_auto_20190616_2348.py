# Generated by Django 2.2.2 on 2019-06-16 23:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nwa', '0006_auto_20190616_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialedge',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outbound', to='nwa.Person'),
        ),
        migrations.AlterField(
            model_name='socialedge',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbound', to='nwa.Person'),
        ),
    ]