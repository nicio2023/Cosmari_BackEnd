from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from django.http import JsonResponse

load_dotenv()
es_client = Elasticsearch([os.getenv("ELASTICSEARCH_URL")],
                          basic_auth=(os.getenv("ELASTICSEARCH_USER"), os.getenv("ELASTICSEARCH_PASSWORD")),
                          verify_certs=False)
