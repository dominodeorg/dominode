# Generated by Django 2.2.15 on 2020-09-25 21:46

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DominodeResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('resource_type', models.CharField(choices=[('document', 'Document'), ('raster', 'Raster'), ('vector', 'Vector'), ('collection', 'Collection'), ('other_resource_type', 'Other')], default='vector', max_length=30)),
                ('artifact_type', models.CharField(choices=[('dataset', 'Dataset'), ('metadata_record', 'Metadata'), ('style', 'Style'), ('other_artifact_type', 'Other')], default='dataset', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ValidationReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('validation_datetime', models.DateTimeField()),
                ('checklist_name', models.CharField(max_length=255)),
                ('checklist_description', models.TextField()),
                ('checklist_steps', django.contrib.postgres.fields.jsonb.JSONField(default=list, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='validation_reports', to='dominode_validation.DominodeResource')),
                ('validator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
