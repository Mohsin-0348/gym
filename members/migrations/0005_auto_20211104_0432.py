# Generated by Django 3.2.8 on 2021-11-04 04:32

import easy_thumbnails.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_auto_20211103_1434'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='food',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='nutritionplan',
            options={'ordering': ['-created_on']},
        ),
        migrations.AlterModelOptions(
            name='trackbodymeasurement',
            options={'ordering': ['-created_on']},
        ),
        migrations.AlterModelOptions(
            name='tracknutritionplan',
            options={'ordering': ['-created_on']},
        ),
        migrations.RemoveField(
            model_name='member',
            name='chest',
        ),
        migrations.RemoveField(
            model_name='member',
            name='height',
        ),
        migrations.RemoveField(
            model_name='member',
            name='hips',
        ),
        migrations.RemoveField(
            model_name='member',
            name='left_arm',
        ),
        migrations.RemoveField(
            model_name='member',
            name='left_calf',
        ),
        migrations.RemoveField(
            model_name='member',
            name='left_thigh',
        ),
        migrations.RemoveField(
            model_name='member',
            name='neck',
        ),
        migrations.RemoveField(
            model_name='member',
            name='right_arm',
        ),
        migrations.RemoveField(
            model_name='member',
            name='right_calf',
        ),
        migrations.RemoveField(
            model_name='member',
            name='right_thigh',
        ),
        migrations.RemoveField(
            model_name='member',
            name='waist',
        ),
        migrations.RemoveField(
            model_name='member',
            name='weight',
        ),
        migrations.AddField(
            model_name='tracknutritionplan',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='uom',
            field=models.CharField(choices=[('gram', 'Gram'), ('piece', 'Piece'), ('litre', 'Litre'), ('calorie', 'Calorie')], max_length=16),
        ),
        migrations.AlterField(
            model_name='nutritionplan',
            name='meal_type',
            field=models.CharField(choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('pre-workout', 'Pre Workout'), ('post-workout', 'Post Workout')], max_length=16),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='chest',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='height',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='hips',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='left_arm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='left_calf',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='left_thigh',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='neck',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='body_measurements/2021-11-04/', verbose_name='ProfilePicture'),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='right_arm',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='right_calf',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='right_thigh',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='waist',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trackbodymeasurement',
            name='weight',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='tracknutritionplan',
            name='photo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='nutrition_plans/2021-11-04/', verbose_name='ProfilePicture'),
        ),
    ]