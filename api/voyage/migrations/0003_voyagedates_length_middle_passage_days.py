# Generated by Django 4.2.1 on 2023-10-26 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voyage', '0002_alter_nationality_name_alter_rigofvessel_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='voyagedates',
            name='length_middle_passage_days',
            field=models.IntegerField(blank=True, null=True, verbose_name='Length of Middle Passage in (days) (VOYAGE)'),
        ),
    ]
