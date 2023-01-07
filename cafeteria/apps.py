from django.apps import AppConfig
from django.conf import settings


class CafeteriaConfig(AppConfig):
    name = 'cafeteria'
    verbose_name = 'Cafeteria Administration'

    def ready(self):
        from cafeteria import scheduler
        if settings.SCHEDULER_AUTOSTART:
            scheduler.start()
