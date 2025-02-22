from rest_framework.decorators import api_view
from rest_framework.response import Response
from .client import es_client
from decorators import jwt_required
import requests
from .utils.validations import check_plate_exists


@api_view(["POST"])
@jwt_required
# Ottiene l'indice richiesto da elastic
def get_index(request):
    index_name = request.data.get("index")
    if not index_name:
        return Response({"error": "Missing 'index' parameter"}, status=400)
    try:
        count_response = es_client.count(index=index_name)
        total_documents = count_response["count"]
        query = {
            "query": {
                "match_all": {}
            },
            "size": total_documents
        }
        response = es_client.search(index=index_name, body=query)
        return Response(response["hits"]["hits"])
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@jwt_required
def create_index(request):
    """
    API per creare un nuovo indice in Elasticsearch basato sulla targa.
    """
    plate_name = request.data.get("plate")
    if not plate_name:
        return Response({"error": "Missing 'index' parameter"}, status=400)
    # Verifica se la targa esiste
    if not check_plate_exists(plate_name):
        return Response({"error": "The plate doesn't exist"}, status=400)

    if es_client.indices.exists(index=plate_name):
        return Response({"error": "This plate had already added"}, status=400)

    es_client.indices.create(index=plate_name)
    return {"message": f"Index {plate_name} successfully created"}



