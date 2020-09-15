# Generated by Django 2.2.15 on 2020-09-15 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('groups', '0034_auto_20200512_1431'),
    ]

    operations = [
        migrations.CreateModel(
            name='CLIGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Rule name')),
                ('command', models.TextField(verbose_name='Command')),
                ('groups', models.ManyToManyField(to='groups.GroupProfile')),
            ],
        ),
    ]
