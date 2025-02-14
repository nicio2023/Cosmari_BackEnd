from rest_framework.decorators import api_view
from rest_framework.response import Response
from .client import es_client

@api_view(["POST"])  
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