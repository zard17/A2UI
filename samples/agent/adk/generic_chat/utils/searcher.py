import logging
import numpy as np
import litellm
from ..templates import TEMPLATES

logger = logging.getLogger(__name__)

class TemplateSearcher:
    def __init__(self, model_name: str = "gemini/text-embedding-004"):
        self.model_name = model_name
        self.templates = []
        self.embeddings = []
        self._index_templates()

    def _index_templates(self):
        """Indexes all available templates by computing their embeddings."""
        logger.info("Indexing templates for semantic search...")
        for key, data in TEMPLATES.items():
            # Skip SIMPLE_MESSAGE as it's always included as a fallback
            if key == "SIMPLE_MESSAGE":
                continue
                
            text_to_embed = f"{data.get('description', '')} {data.get('keywords', '')}"
            try:
                # Synchronous embedding call for startup simplicity
                response = litellm.embedding(model=self.model_name, input=[text_to_embed])
                embedding = response.data[0]["embedding"]
                
                self.templates.append({
                    "id": key,
                    "description": data.get("description", ""),
                    "full_data": data
                })
                self.embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed template {key}: {e}")

        self.embeddings = np.array(self.embeddings)
        logger.info(f"Indexed {len(self.templates)} templates.")

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Retrieves top_k most relevant templates for the query.
        Always returns the candidate list, which should be used to filter the prompt.
        """
        if not self.templates:
            return []

        try:
            response = litellm.embedding(model=self.model_name, input=[query])
            query_embedding = np.array(response.data[0]["embedding"])
            
            # Cosine similarity
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get top K indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = [self.templates[i]["id"] for i in top_indices]
            logger.info(f"Search results for '{query}': {results}")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Fallback: return empty list or some default
            return []
