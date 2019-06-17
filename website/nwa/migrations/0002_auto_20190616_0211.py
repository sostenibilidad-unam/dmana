# Generated by Django 2.2.2 on 2019-06-16 02:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nwa', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agencyedge',
            options={'verbose_name_plural': 'Agency Edgelist'},
        ),
        migrations.AlterModelOptions(
            name='mentaledge',
            options={'verbose_name_plural': 'Cognitive map Edgelist'},
        ),
        migrations.AlterModelOptions(
            name='poweredge',
            options={'verbose_name_plural': 'Avatar power Edgelist'},
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=200)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Organizations',
            },
        ),
        migrations.AddField(
            model_name='person',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nwa.Organization'),
        ),
    ]
