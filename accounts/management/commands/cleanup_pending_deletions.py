from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete user accounts that have passed the 3-day deletion period'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # Find all accounts pending deletion where the deletion time has passed
        now = timezone.now()
        users_to_delete = User.objects.filter(
            is_pending_deletion=True,
            deletion_scheduled_at__lte=now
        )
        
        count = users_to_delete.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {count} account(s)')
            )
            for user in users_to_delete:
                self.stdout.write(f'  - {user.username} ({user.email})')
            return
        
        # Delete each user
        deleted_count = 0
        for user in users_to_delete:
            try:
                username = user.username
                email = user.email
                
                # Send final deletion email
                try:
                    email_context = {
                        'username': username,
                        'date': timezone.now().strftime('%B %d, %Y at %H:%M %Z'),
                    }
                    email_html = render_to_string(
                        'accounts/email/account_deletion_confirmation.html',
                        email_context
                    )
                    send_mail(
                        '❌ Account Permanently Deleted - JnDroid Store',
                        'Your account has been permanently deleted.',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        html_message=email_html,
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send final deletion email to {email}: {str(e)}")
                
                # Delete the user
                user.delete()
                deleted_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Deleted account: {username} ({email})')
                )
            except Exception as e:
                logger.error(f"Error deleting user {user.username}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to delete {user.username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully deleted {deleted_count} account(s)')
        )
