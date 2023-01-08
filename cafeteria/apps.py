from django.apps import AppConfig
from django.db.backends.signals import connection_created


class CafeteriaConfig(AppConfig):
    name = 'cafeteria'
    verbose_name = 'Cafeteria Administration'

    def ready(self):
        from cafeteria.scheduler import start_scheduler
        connection_created.connect(start_scheduler, sender=self)
