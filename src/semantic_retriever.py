
import numpy as np
from sentence_transformers import SentenceTransformer

from src.note_retriever import retrieve_notes


class SemanticNoteRetriever:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, notes):
        self.notes = notes.copy()
        self.model = SentenceTransformer(self.MODEL_NAME)

        # Encode all 10 notes once, rather than
        # re-encoding them for every anomaly.
        self.note_ids = self.notes["note_id"].astype(str).tolist()

        texts = [
            (
                f"Route: {row['applies_to']}. "
                f"Date: {row['date']}. "
                f"Context: {row['note']}"
            )
            for _, row in self.notes.iterrows()
        ]

        self.embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        self.id_to_index = {
            note_id: index
            for index, note_id in enumerate(self.note_ids)
        }

    def search(self, route, week_of, top_k=10):
        # Keep the original route/date constraints.
        # Semantic retrieval cannot override them.
        candidates = retrieve_notes(
            route=route,
            week_of=week_of,
            notes=self.notes
        )

        if not candidates:
            return []

        query = (
            f"Transportation freight cost increase "
            f"on the {route} route during the week "
            f"starting {week_of}. Find contextual "
            f"evidence explaining higher shipping "
            f"costs, including fuel prices, weather, "
            f"festivals, road disruptions and tolls."
        )

        query_embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        results = []

        for candidate in candidates:
            idx = self.id_to_index[candidate["note_id"]]

            similarity = float(
                np.dot(
                    query_embedding,
                    self.embeddings[idx]
                )
            )

            result = candidate.copy()
            result["similarity_score"] = similarity
            results.append(result)

        # Highest semantic similarity first.
        results.sort(
            key=lambda x: (
                -x["similarity_score"],
                x["note_id"]
            )
        )

        return results[:top_k]
