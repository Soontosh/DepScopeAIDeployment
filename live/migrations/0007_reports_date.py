# Generated by Django 4.2.10 on 2024-03-19 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live', '0006_reports_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='reports',
            name='date',
            field=models.CharField(default='3/17/2024', max_length=10),
            preserve_default=False,
        ),
    ]