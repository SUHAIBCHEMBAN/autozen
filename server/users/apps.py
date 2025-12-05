"""
App configuration for the users app.

This module defines the app configuration and ensures signals are loaded.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    App configuration class for the users app.
    
    Ensures proper loading of signals and sets the default auto field.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """
        Method called when the app is ready.
        
        Imports models to ensure signals are connected.
        """
        import users.models  # noqa
