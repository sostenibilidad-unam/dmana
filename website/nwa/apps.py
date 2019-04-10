from django.apps import AppConfig


class NwaConfig(AppConfig):
    name = 'nwa'
    verbose_name = 'NetWork Arquitect'

    def ready(self):
        import nwa.signals
