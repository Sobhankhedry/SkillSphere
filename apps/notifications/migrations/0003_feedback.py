import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='link',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('severity', models.CharField(choices=[('success', 'Success'), ('error', 'Error'), ('warning', 'Warning'), ('info', 'Info')], max_length=10)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('action', models.CharField(blank=True, default='', max_length=100)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'feedbacks',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'is_read', '-created_at'], name='idx_feedback_user_read'),
                ],
            },
        ),
    ]
