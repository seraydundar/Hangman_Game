# Generated by Django 5.1.6 on 2025-02-19 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_remove_word_hint'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
