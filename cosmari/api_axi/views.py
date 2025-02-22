from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from decorators import jwt_required
from utils import handle_api_response

# Variabili globali per memorizzare il token e la lista delle targhe
saved_token = None
plates = None
load_dotenv()


# Questa funzione mi serve per ottenere un nuovo token quando quello vecio è scaduto
def refresh_token():
    global saved_token
    token_url = "https://api.axitea.it/api/Auth/GetToken"
    payload = {
        "codiceCliente": os.getenv("CLIENT_CODE")
    }
    try:
        response = requests.post(token_url, json=payload)
        if response.status_code == 200:
            cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
            json_data = json.loads(cleaned_text)
            saved_token = json_data.get("clientId")
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
    token_url = "https://api.axitea.it/api/Auth/GetToken"
    payload = {
        "codiceCliente": os.getenv("CLIENT_CODE")
    }
    try:
        response = requests.post(token_url, json=payload)
        if response.status_code == 200:
            cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
            json_data = json.loads(cleaned_text)
            saved_token = json_data.get("clientId")
            return JsonResponse({"status": "success", "token": saved_token})
        else:
            return JsonResponse({"status": "error", "message": "Errore nella richiesta del token"}, status=response.status_code)
    except Exception as e:
        print("Errore durante la richiesta del token:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Vista per ottenere la lista delle targhe
@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_plates(request):
    global plates, saved_token
    if plates:
        return JsonResponse({"status": "success", "data": plates})
    try:
        if not saved_token:
            saved_token = refresh_token()
        plates_url = "https://api.axitea.it/api/Vehicle/GetMyVehicles"
        payload = {"clientid": saved_token}
        headers = {"Content-Type": "application/json"}
        response = requests.post(plates_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
        if json_data:
            plates = json_data
            return JsonResponse({"status": "success", "data": plates})
        else:
            return JsonResponse({"status": "error", "message": "Errore nel recupero delle targhe"}, status=500)
    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto":
            saved_token = refresh_token()
            return get_vehicle_plates(request)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Vista per ottenere i dettagli di un veicolo
@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_details(request):
    global saved_token
    try:
        if not saved_token:
            saved_token = refresh_token()
        data = json.loads(request.body)
        plate = data.get("plate")
        datestart = data.get("datestart")
        dateend = data.get("dateend")
        if not plate or not datestart or not dateend:
            return JsonResponse({"status": "error", "message": "Parametri mancanti"}, status=400)
        details_url = "https://api.axitea.it/api/Vehicle/GetMyVehiclesDetails"
        payload = {
            "clientId": saved_token,
            "plate": plate,
            "datestart": datestart,
            "dateend": dateend
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(details_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
        if json_data:
            return JsonResponse({"status": "success", "data": json_data})
        else:
            return JsonResponse({"status": "error", "message": "Errore nel recupero dei dettagli"}, status=500)
    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto":
            saved_token = refresh_token()
            return get_vehicle_details(request)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Vista per ottenere le informazioni sulla flotta di veicoli
@csrf_exempt
@require_http_methods(["POST"])
def get_my_vehicles_info(request):
    global saved_token
    try:
        if not saved_token:
            saved_token = refresh_token()
        info_url = "https://api.axitea.it/api/Vehicle/GetMyVehiclesInfo"
        payload = {
            "codiceCliente": os.getenv("CLIENT_CODE"),
            "clientId": saved_token
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(info_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
        if json_data:
            return JsonResponse({"status": "success", "data": json_data})
        else:
            return JsonResponse({"status": "error", "message": "Errore nel recupero delle informazioni sui veicoli"}, status=500)
    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto" or str(e) == "Token scaduto o errore generico":
            saved_token = None
            saved_token = refresh_token()
            return get_my_vehicles_info(request)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Vista per ottenere i dettagli di un veicolo con ritardo
@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_details_with_delay(request):
    global saved_token
    try:
        if not saved_token:
            saved_token = refresh_token()
        data = json.loads(request.body)
        plate = data.get("plate")
        datestart = data.get("datestart")
        dateend = data.get("dateend")
        if not plate or not datestart or not dateend:
            return JsonResponse({"status": "error", "message": "Parametri mancanti"}, status=400)
        details_url = "https://api.axitea.it/api/Vehicle/GetMyVehiclesWithDelay"
        payload = {
            "clientId": saved_token,
            "plate": plate,
            "datestart": datestart,
            "dateend": dateend
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(details_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
        if json_data:
            return JsonResponse({"status": "success", "data": json_data})
        else:
            return JsonResponse({"status": "error", "message": "Errore nel recupero dei dettagli con ritardo"}, status=500)
    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto":
            saved_token = refresh_token()
            return get_vehicle_details_with_delay(request)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_info_by_interval(request):
    global saved_token
    try:
        if not saved_token:
            saved_token = refresh_token()
        data = json.loads(request.body)
        plate = data.get("plate")
        datestart = data.get("datestart")
        dateend = data.get("dateend")
        if not plate or not datestart or not dateend:
            return JsonResponse({"status": "error", "message": "Parametri mancanti"}, status=400)
        details_url = "https://api.axitea.it/api/Vehicle/GetInfoVehicleByInterval"
        payload = {
            "clientId": saved_token,
            "plate": plate,
            "datestart": datestart,
            "dateend": dateend
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(details_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
        if json_data:
            return JsonResponse({"status": "success", "data": json_data})
        else:
            return JsonResponse({"status": "error", "message": "Errore nel recupero dei dettagli con intervallo"}, status=500)
    except ValueError as e:
        print(f"Errore: {e}")
        if str(e) == "Token scaduto":
            saved_token = refresh_token()
            return get_vehicle_details_with_delay(request)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)