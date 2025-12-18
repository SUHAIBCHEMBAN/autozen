from django.apps import AppConfig


class AdminCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_custom'
    
    def ready(self):
        # Import the admin module to register the custom admin site
        import admin_custom.admin