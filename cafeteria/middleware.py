from django.core.cache import cache
from django.utils import timezone

from transactions.models import Transaction


class ClearLimitedItemsCache:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_cache_clear = timezone.localdate()

    def __call__(self, request):
        # cache.clear()
        if not Transaction.accepting_orders():
            cache.clear()
            self.last_cache_clear = timezone.localdate()

        response = self.get_response(request)
        return response
