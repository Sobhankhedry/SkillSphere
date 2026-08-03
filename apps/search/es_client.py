from django.conf import settings
from elasticsearch_dsl import connections


def get_es_client():
    connections.create_connection(alias="default", hosts=[settings.ELASTICSEARCH_URL])
    return connections.get_connection("default")
