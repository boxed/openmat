# Generated by Django 4.1 on 2022-09-10 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openmat', '0003_topic_user_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='belt',
            field=models.CharField(choices=[('white', 'white'), ('blue', 'blue'), ('purple', 'purple'), ('brown', 'brown'), ('black', 'black')], max_length=255, null=True),
        ),
    ]
