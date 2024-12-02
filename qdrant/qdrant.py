from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

qdrant_client = QdrantClient(
    url="https://6a5312bf-a920-470a-93c6-c5e6885e1902.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="Dq1_lDlXsEL8FzYUdtdGanSThTUxh7LmHgVreKxECUA1uCzZt6SUlw",
)

# collection is already made
# qdrant_client.create_collection(
#     collection_name="comp670",
#     vectors_config=VectorParams(size=100, distance=Distance.COSINE),
# )

