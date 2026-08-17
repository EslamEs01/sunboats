from django.utils import translation


class AdminArabicMiddleware:
    """Public site stays English. Jazzmin /admin/ is Arabic for the staff user."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin"):
            translation.activate("ar")
            request.LANGUAGE_CODE = "ar"
            response = self.get_response(request)
            response.headers.setdefault("Content-Language", "ar")
            translation.deactivate()
            return response
        return self.get_response(request)
