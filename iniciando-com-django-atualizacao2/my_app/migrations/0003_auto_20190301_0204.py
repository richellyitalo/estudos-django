# Generated by Django 2.1.7 on 2019-03-01 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_post_subtitle'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name': 'Artigo'},
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(verbose_name='Conteúdo'),
        ),
        migrations.AlterField(
            model_name='post',
            name='subtitle',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Subtítulo'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Título'),
        ),
    ]
