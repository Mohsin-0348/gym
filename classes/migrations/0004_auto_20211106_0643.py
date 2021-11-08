# Generated by Django 3.2.8 on 2021-11-06 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_auto_20211106_0526'),
        ('classes', '0003_alter_weekday_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseclass',
            name='gender_type',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('not-specified', 'Not Specified')], default='not-specified', max_length=16),
        ),
        migrations.AlterUniqueTogether(
            name='classbooking',
            unique_together={('scheduled_class', 'member')},
        ),
    ]