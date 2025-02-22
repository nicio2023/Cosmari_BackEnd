from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from decorators import jwt_required
from utils import validate_date_range
from utils import handle_api_response

# Variabili globali per memorizzare il token e la lista delle targhe
saved_token = None
plates = None
load_dotenv()




# Questa funzione mi serve per ottenere un nuovo token quando quello vecio è scaduto
def refresh_token():
    global saved_token
    token_url = "https://prod.backendkeplero.assist-web.eu:8443/keplero/public/token.kpl"
    payload = {
        "user": os.getenv("USER_BUCHER"),
        "pwd": os.getenv("PWD_BUCHER")
    }
    try:
        response = requests.post(token_url, json=payload)
        if response.status_code == 200:
            cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
            json_data = json.loads(cleaned_text)
            saved_token = json_data.get("token")
            return saved_token
        else:
            return "Errore nella richiesta del token"
    except Exception as e:
        print("Errore durante la richiesta del token:", e)


# Vista per ottenere il token
@csrf_exempt
@require_http_methods(["POST"])
def get_api_token(request):
    global saved_token
    token_url = "https://prod.backendkeplero.assist-web.eu:8443/keplero/public/token.kpl"
    payload = {
        "user": os.getenv("USER_BUCHER"),
        "pwd": os.getenv("PWD_BUCHER")
    }
    try:
        response = requests.post(token_url, json=payload)
        if response.status_code == 200:
            cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
            json_data = json.loads(cleaned_text)
            saved_token = json_data.get("token")
            return JsonResponse({"status": "success", "token": saved_token})
        else:
            return JsonResponse({"status": "error", "message": "Errore nella richiesta del token"}, status=response.status_code)
    except Exception as e:
        print("Errore durante la richiesta del token:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_mission_data(request):
    global saved_token

    try:
        # Recupera i parametri GET dalla richiesta
        starttime = request.GET.get("starttime")
        endtime = request.GET.get("endtime")
        snmachine = request.GET.getlist("snmachine")  # Otteniamo una lista di serial number

        # Controllo validità dell'intervallo di date
        if starttime and endtime and not validate_date_range(starttime, endtime,1,7):
            return JsonResponse({"status": "error", "message": "Intervallo di date non valido (deve essere tra 1 e 7 giorni)"}, status=400)

        # Se il token non è disponibile o è scaduto, aggiorniamolo
        if not saved_token:
            saved_token = refresh_token()

        # URL dell'API di GetMission
        mission_url = "https://prod.backendkeplero.assist-web.eu:8443/keplero/mission/getMission.kpl"

        # Creazione dei parametri della richiesta
        params = {}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime
        if snmachine:  # Solo se snmachine è fornito
            params["snmachine"] = ",".join(snmachine)  # Unisci la lista in una stringa separata da virgole

        # Header con il token di autenticazione
        headers = {
            "X-Auth-Token": saved_token,
        }

        # Invio della richiesta GET all'API
        response = requests.get(mission_url, params=params, headers=headers)

        # Gestione della risposta con la funzione handle_api_response
        json_data = handle_api_response(response)

        if json_data:
            return JsonResponse({"status": "success", "data": json_data})

        return JsonResponse({"status": "error", "message": "Nessun dato restituito"}, status=404)

    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto":
            saved_token = refresh_token()
            return get_assets_tracking(request)  # Riprova con il nuovo token
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_assets_tracking(request):
    global saved_token

    try:
        # Recupero dei parametri GET con conversione forzata a stringa (evita liste)
        starttime = request.GET.get("starttime", "").strip()
        endtime = request.GET.get("endtime", "").strip()

        print(f"starttime: {starttime} ({type(starttime)})")
        print(f"endtime: {endtime} ({type(endtime)})")

        # Controllo validità dell'intervallo di date
        if starttime and endtime and not validate_date_range(starttime, endtime, 1, 3):
            return JsonResponse(
                {"status": "error", "message": "Intervallo di date non valido (deve essere tra 1 e 3 giorni)"},
                status=400)

        # Se il token non è disponibile o è una lista (errore), aggiorniamolo
        if not saved_token:
            saved_token = refresh_token()

        # URL dell'API di Keplero
        tracking_url = "https://prod.backendkeplero.assist-web.eu:8443/keplero/mission/getDataAssetsTracking.kpl"

        # Creazione dei parametri della richiesta
        params = {}
        if starttime:
            params["starttime"] = starttime
        if endtime:
            params["endtime"] = endtime

        # Header con il token di autenticazione
        headers = {
            "X-Auth-Token": saved_token,
        }

        # Invio della richiesta GET all'API
        response = requests.get(tracking_url, params=params, headers=headers)

        # Gestione della risposta
        json_data = handle_api_response(response)

        if json_data:
            return JsonResponse({"status": "success", "data": json_data})

        return JsonResponse({"status": "error", "message": "Nessun dato restituito"}, status=404)

    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto":
            saved_token = refresh_token()
            return get_assets_tracking(request)  # Riprova con il nuovo token
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    except Exception as e:
        print(f"Eccezione generica: {e}")  # Debug
        return JsonResponse({"status": "error", "message": str(e)}, status=500)