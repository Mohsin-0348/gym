# Generated by Django 3.2.8 on 2021-11-15 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0005_alter_classworkout_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeattendance',
            name='check_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gymattendance',
            name='check_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]