# Generated by Django 3.1.2 on 2020-11-21 06:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogtype',
            old_name='blog_type',
            new_name='type_name',
        ),
    ]
