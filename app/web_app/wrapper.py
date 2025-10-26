import requests

class QdrantClientWrapper:
    def __init__(self, host="qdrant", port=6333):
        self.base = f"http://{host}:{port}"
        self.collection = "items"
        r = requests.get(f"{self.base}/collections/{self.collection}")
        if r.status_code == 404:
            requests.put(f"{self.base}/collections/{self.collection}", json={
                "vectors": {"size": 128, "distance": "Cosine"}
            }) 

    def upsert_point(self, id, vector, payload=None):
        data = {"points":[{"id": id, "vector": vector, "payload": payload}]}
        return requests.post(f"{self.base}/collections/{self.collection}/points", json=data).json()

    def search_by_vector(self, vector, top=5):
        data = {"vector": vector, "limit": top}
        return requests.post(f"{self.base}/collections/{self.collection}/points/search", json=data).json()