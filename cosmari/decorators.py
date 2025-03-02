from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.decorators import method_decorator


def jwt_required(view_func):
    """Decoratore per proteggere gli endpoint con JWT estratto dal cookie. Un pò come il gestore di stato in aspnet solo che mi tocca farlo manualmente """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.COOKIES.get("access_token"):
            return JsonResponse({"status": "error", "message": "Non sei autenticato"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view
