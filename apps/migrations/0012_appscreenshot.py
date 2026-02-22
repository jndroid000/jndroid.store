# Generated migration for AppScreenshot model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0011_appdownload_favorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppScreenshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Screenshot image (recommended: 1080x1920 or similar)', upload_to='app_screenshots/')),
                ('caption', models.CharField(blank=True, help_text='Optional caption/description', max_length=200)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order (lower = first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(help_text='App this screenshot belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='screenshots', to='apps.app')),
            ],
            options={
                'verbose_name': 'App Screenshot',
                'verbose_name_plural': 'App Screenshots',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
