import json
from datetime import datetime, timezone


def handle_api_response(response):
    """
    Gestisce la risposta dell'API, rimuove il BOM e verifica lo status code.
    Se il token è scaduto o si verifica un errore generico, solleva un'eccezione.
    """
    global saved_token
    try:
        cleaned_text = response.text.encode('utf-8').decode('utf-8-sig')
        json_data = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print("Errore nel parsing JSON:", e)
        return None

    # DEBUG: Stampa il tipo di json_data
    print(f"Tipo di json_data: {type(json_data)}")

    if response.status_code != 200:
        print(f"Errore nella richiesta. Status code: {response.status_code}")
        if isinstance(json_data, dict):  # Evitiamo errori se è una lista
            if json_data.get("Message") == "An error has occurred.":
                print("Errore generico dell'API, possibile token scaduto")
                raise ValueError("Token scaduto")
            if json_data.get("errorMessage") == "AccountInfo is not valid":
                print("Token scaduto o non valido")
                raise ValueError("Token scaduto")
        raise ValueError(f"Errore non gestito: {response.text}")

    # Controllo specifico per errori legati al token
    if isinstance(json_data, dict) and json_data.get("errorMessage") == "AccountInfo is not valid":
        print("Token scaduto o non valido")
        saved_token = None
        raise ValueError("Token scaduto")

    return json_data  # Può essere una lista o un dizionario


def validate_date_range(starttime, endtime, firstday, lastday):
    """
       Verifica che l'intervallo tra starttime ed endtime sia compreso tra min_days e max_days.
       Considera anche intervalli inferiori a 24 ore come validi.
       """
    if not starttime or not endtime:
        return True  # Se uno dei due è assente, non facciamo la validazione

    # Converti i timestamp in oggetti datetime
    start_date = datetime.fromtimestamp(starttime, tz=timezone.utc)
    end_date = datetime.fromtimestamp(endtime, tz=timezone.utc)

    delta = end_date - start_date

    return firstday <= delta.total_seconds() / 86400 <= lastday