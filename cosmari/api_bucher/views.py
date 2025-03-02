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
        starttime_str = request.GET.get('starttime')
        endtime_str = request.GET.get('endtime')
        snmachine = request.GET.getlist("snmachine")  # Otteniamo una lista di serial number

        try:
            #Converti le stringhe in interi
            starttime = int(starttime_str)
            endtime = int(endtime_str)
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "starttime e endtime devono essere numeri validi."},
                                status=400)

        # Controllo validità dell'intervallo di date
        if starttime and endtime and not validate_date_range(starttime, endtime,0,7):
            return JsonResponse({"status": "error", "message": "Intervallo di date non valido (deve essere tra 1 e 7 giorni)"}, status=400)

        # Se il token non è disponibile o è scaduto, aggiorniamolo
        if not saved_token:
            saved_token = refresh_token()

        # URL dell'API di GetMission
        mission_url = "https://prod.backendkeplero.assist-web.eu:8443/keplero/mission/getMission.kpl"

        # Creazione dei parametri della richiesta
        params = {}
        if starttime:
            params["starttime"] = starttime_str
        if endtime:
            params["endtime"] = endtime_str
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

        starttime_str = request.GET.get('starttime')
        endtime_str = request.GET.get('endtime')

        print(f"starttime: {starttime_str} ({type(starttime_str)})")
        print(f"endtime: {endtime_str} ({type(endtime_str)})")

        try:
            # Converti le stringhe in interi
            starttime = int(starttime_str)
            endtime = int(endtime_str)
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "starttime e endtime devono essere numeri validi."},
                                status=400)

        # Controllo validità dell'intervallo di date
        if starttime and endtime and not validate_date_range(starttime, endtime, 0, 3):
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
            params["starttime"] = starttime_str
        if endtime:
            params["endtime"] = endtime_str

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