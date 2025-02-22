import requests

PLATES_API_URL = "http://localhost:8000/api/plates/"

def check_plate_exists(targa: str) -> bool:
    """
    Controlla se la targa esiste nell'API delle targhe.
    """
    try:
        response = requests.get(PLATES_API_URL)
        if response.status_code == 200:
            data = response.json()
            plates = data.get("data", [])
            return targa in plates
        return False
    except requests.RequestException:
        return False