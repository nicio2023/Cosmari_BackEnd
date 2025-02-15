from datetime import datetime, timedelta
import requests
import json
from dotenv import load_dotenv
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

load_dotenv()
saved_token = None
plates = None

def handle_api_response(response):
    """
    Gestisce la risposta dell'API, rimuove il BOM e verifica lo status code.
    Se il token è scaduto, solleva un'eccezione per richiederne uno nuovo.
    """
    try:
        cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
        json_data = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print("Errore nel parsing JSON:", e)
        return None
    if response.status_code != 200:
        print(f"Errore nella richiesta. Status code: {response.status_code}")
        if response.status_code == 500 and json_data.get("error") and json_data.get("errorMessage") == "AccountInfo is not valid":
            print("Token scaduto")
            raise ValueError("Token scaduto")
        else:
            raise ValueError(f"Errore non gestito: {response.text}")
    return json_data

@csrf_exempt
@require_http_methods(["POST"])
def get_api_token(request):
    """
    Vista per ottenere il token dall'API.
    """
    global saved_token
    token_url = "https://api.axitea.it/api/Auth/GetToken"
    payload = {
        "codice_cliente": os.getenv("CLIENT_CODE")
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        try:
            cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
            json_data = json.loads(cleaned_text)
            saved_token = json_data.get("clientId")
            return JsonResponse({"status": "success", "token": saved_token})
        except json.JSONDecodeError as e:
            print("Errore nel parsing JSON:", e)
            return JsonResponse({"status": "error", "message": "Errore nel parsing della risposta"}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Errore nel recupero del token"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_plates(request):
    """
    Vista per ottenere la lista delle targhe dei veicoli.
    """
    global plates, saved_token
    if plates:
        return JsonResponse({"status": "success", "data": plates})
    if not saved_token:
        saved_token = get_api_token(request).content.decode('utf-8')  # Ottieni il token dalla risposta
    plates_url = "https://api.axitea.it/api/Vehicle/GetMyVehicles"
    payload = {
        "clientid": saved_token
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(plates_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
    except ValueError as e:
        if str(e) == "Token scaduto":
            saved_token = None
            saved_token = get_api_token(request).content.decode('utf-8')
            response = requests.post(plates_url, json=payload, headers=headers)
            json_data = handle_api_response(response)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    if json_data:
        plates = json_data
        return JsonResponse({"status": "success", "data": plates})
    else:
        return JsonResponse({"status": "error", "message": "Errore nel recupero delle targhe"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_details(request):
    """
    Vista per ottenere i dettagli di un veicolo in un range temporale.
    """
    global saved_token
    if not saved_token:
        saved_token = get_api_token(request).content.decode('utf-8')
    try:
        data = json.loads(request.body)
        plate = data.get("plate")
        datestart = data.get("datestart")
        dateend = data.get("dateend")
        if not plate or not datestart or not dateend:
            return JsonResponse({"status": "error", "message": "Parametri mancanti"}, status=400)
    except json.JSONDecodeError as e:
        return JsonResponse({"status": "error", "message": "Errore nel parsing del corpo della richiesta"}, status=400)

    details_url = "https://api.axitea.it/api/Vehicle/GetMyVehiclesDetails"
    payload = {
        "clientId": saved_token,
        "plate": plate,
        "datestart": datestart,
        "dateend": dateend
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(details_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
    except ValueError as e:
        if str(e) == "Token scaduto":
            saved_token = None
            saved_token = get_api_token(request).content.decode('utf-8')
            response = requests.post(details_url, json=payload, headers=headers)
            json_data = handle_api_response(response)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    if json_data:
        return JsonResponse({"status": "success", "data": json_data})
    else:
        return JsonResponse({"status": "error", "message": "Errore nel recupero dei dettagli"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_vehicle_details_with_delay(request):
    """
    Vista per ottenere i dettagli di un veicolo con ritardo in un range temporale.
    """
    global saved_token
    if not saved_token:
        saved_token = get_api_token(request).content.decode('utf-8')
    try:
        data = json.loads(request.body)
        plate = data.get("plate")
        datestart = data.get("datestart")
        dateend = data.get("dateend")
        if not plate or not datestart or not dateend:
            return JsonResponse({"status": "error", "message": "Parametri mancanti"}, status=400)
    except json.JSONDecodeError as e:
        return JsonResponse({"status": "error", "message": "Errore nel parsing del corpo della richiesta"}, status=400)

    details_url = "https://api.axitea.it/api/Vehicle/GetMyVehiclesWithDelay"
    payload = {
        "clientId": saved_token,
        "plate": plate,
        "datestart": datestart,
        "dateend": dateend
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(details_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
    except ValueError as e:
        if str(e) == "Token scaduto":
            saved_token = None
            saved_token = get_api_token(request).content.decode('utf-8')
            response = requests.post(details_url, json=payload, headers=headers)
            json_data = handle_api_response(response)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    if json_data:
        return JsonResponse({"status": "success", "data": json_data})
    else:
        return JsonResponse({"status": "error", "message": "Errore nel recupero dei dettagli con ritardo"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_my_vehicles_info(request):
    """
    Vista per ottenere le informazioni sulla flotta di veicoli.
    """
    global saved_token
    if not saved_token:
        saved_token = get_api_token(request).content.decode('utf-8')
    info_url = "https://api.axitea.it/api/Vehicle/GetMyVehiclesInfo"
    payload = {
        "codiceCliente": os.getenv("CLIENT_CODE"),
        "clientId": saved_token
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(info_url, json=payload, headers=headers)
        json_data = handle_api_response(response)
    except ValueError as e:
        if str(e) == "Token scaduto":
            saved_token = None
            saved_token = get_api_token(request).content.decode('utf-8')
            response = requests.post(info_url, json=payload, headers=headers)
            json_data = handle_api_response(response)
        else:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    if json_data:
        return JsonResponse({"status": "success", "data": json_data})
    else:
        return JsonResponse({"status": "error", "message": "Errore nel recupero delle informazioni sui veicoli"}, status=500)