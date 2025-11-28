# Generated manually due to drf_yasg import issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_managers'),  # Depends on the existing 0009
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='welcome_email_sent',
            field=models.BooleanField(default=False, help_text='Whether welcome email was successfully sent'),
        ),
        migrations.AddField(
            model_name='user',
            name='welcome_email_sent_at',
            field=models.DateTimeField(blank=True, help_text='When welcome email was sent', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='welcome_email_attempts',
            field=models.IntegerField(default=0, help_text='Number of attempts to send welcome email'),
        ),
        migrations.AddField(
            model_name='user',
            name='welcome_email_last_error',
            field=models.TextField(blank=True, help_text='Last error when sending welcome email', null=True),
        ),
    ]

