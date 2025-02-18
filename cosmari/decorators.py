from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.decorators import method_decorator


def jwt_required(view_func):
    """Decoratore per proteggere gli endpoint con JWT estratto dal cookie. Un pò come il gestore di stato in aspnet solo che mi tocca farlo manualmente """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get("access_token")
        if not token:
            return JsonResponse({"status": "error", "message": "Token mancante"}, status=401)
        try:
            access_token = AccessToken(token)  # Verifica il token JWT
            request.user = access_token["user_id"]  # Associa l'utente alla richiesta
        except Exception:
            return JsonResponse({"status": "error", "message": "Token non valido o scaduto"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view
