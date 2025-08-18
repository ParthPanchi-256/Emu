# FAISS for vector similarity search
import faiss
import io
from typing import List, Dict, Any, Tuple
from src.log import logger
from PIL import Image
from sentence_transformers import SentenceTransformer

class MultimodalVectorStore:
    def __init__(self, model_name: str):
        self.embed_model = SentenceTransformer(model_name)

        text_emb = self.embed_model.encode(['your text query'])
        d = text_emb.shape[1]
        self.dimension = d
        self.text_index = faiss.IndexFlatL2(self.dimension)
        self.image_index = faiss.IndexFlatL2(self.dimension)
        self.text_documents = []
        self.image_documents = []

    def add_documents(self, documents: List[Dict[str, Any]]):
        if not documents:
            return

        doc_type = documents[0]["metadata"]["type"]
        contents = [doc["content"] for doc in documents]

        if doc_type == "text":
            embeddings = self.embed_model.encode(contents).astype('float32')
            self.text_index.add(embeddings)
            self.text_documents.extend(documents)
            logger.info(f"Added {len(documents)} text documents.")
        elif doc_type == "image":
            # For images, we need to convert to PIL format for the embedding model
            pil_images = [Image.open(io.BytesIO(c)) for c in contents]
            embeddings = self.embed_model.encode(pil_images).astype('float32')
            self.image_index.add(embeddings)
            self.image_documents.extend(documents)
            logger.info(f"Added {len(documents)} image documents.")

    def retrieve(self, query: str, top_k_text: int, top_k_images: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        query_embedding = self.embed_model.encode(query).astype('float32').reshape(1, -1)

        # Retrieve text
        text_results = []
        if self.text_index.ntotal > 0:
            distances, indices = self.text_index.search(query_embedding, min(top_k_text, self.text_index.ntotal))
            for i, idx in enumerate(indices[0]):
                if idx < len(self.text_documents):
                    result_doc = self.text_documents[idx].copy()
                    result_doc['relevance_score'] = 1.0 / (1.0 + distances[0][i])
                    text_results.append(result_doc)

        # Retrieve images
        image_results = []
        if self.image_index.ntotal > 0:
            distances, indices = self.image_index.search(query_embedding, min(top_k_images, self.image_index.ntotal))
            for i, idx in enumerate(indices[0]):
                if idx < len(self.image_documents):
                    result_doc = self.image_documents[idx].copy()
                    result_doc['relevance_score'] = 1.0 / (1.0 + distances[0][i])
                    image_results.append(result_doc)

        return text_results, image_results