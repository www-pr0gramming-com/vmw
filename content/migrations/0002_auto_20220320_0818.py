# Generated by Django 3.2.12 on 2022-03-20 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='video',
            name='order',
            field=models.IntegerField(default=1),
        ),
    ]
