# Generated by Django 4.0.2 on 2022-07-27 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0005_alter_doc_citation'),
        ('voyage', '0012_voyagesourcesconnection_doc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voyagesourcesconnection',
            name='doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='docs.doc'),
        ),
    ]
