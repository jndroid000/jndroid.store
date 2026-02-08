from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    
    def ready(self):
        """Register signals when app is ready"""
        import accounts.signals  # noqa

