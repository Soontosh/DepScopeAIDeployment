# Generated by Django 4.2.10 on 2024-03-19 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live', '0007_reports_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='reports',
            name='image',
            field=models.ImageField(default='defaults/default.png', upload_to='reports/'),
        ),
    ]
