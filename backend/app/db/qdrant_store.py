from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_ollama import OllamaEmbeddings
from langchain_community.docstore.document import Document
from app.config import QDRANT_URL, QDRANT_API_KEY, OLLAMA_EMBED_MODEL
import uuid
import os

class QdrantVectorStore:
    def __init__(self):
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY
        )
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.embeddings = OllamaEmbeddings(
            model=OLLAMA_EMBED_MODEL,
            base_url=base_url
        )
    
    def create_collection(self, collection_name: str, vector_size: int = 768):
        """Create a new collection for a lecture"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            # Collection might already exist
            print(f"Collection {collection_name} creation: {e}")
    
    def add_texts(self, collection_name: str, texts: List[str], metadata: List[Dict[str, Any]] = None):
        """Add text chunks to collection with metadata"""
        if metadata is None:
            metadata = [{} for _ in texts]
        
        # Generate embeddings
        embeddings = self.embeddings.embed_documents(texts)
        
        # Create points for Qdrant
        points = []
        for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    **meta
                }
            )
            points.append(point)
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    def similarity_search(
        self,
        collection_name: str,
        query: str,
        k: int = 4,
        user_id: Optional[int] = None,
        course_id: Optional[int] = None
    ) -> List[Document]:
        """Search for similar texts with optional filtering."""
        
        # 1️⃣ Generate embedding for the query
        query_embedding = self.embeddings.embed_query(query)

        # 2️⃣ Build filter if needed
        query_filter = None
        if user_id is not None or course_id is not None:
            conditions = []
            if user_id is not None:
                conditions.append(FieldCondition(key="user_id", match=MatchValue(value=user_id)))
            if course_id is not None:
                conditions.append(FieldCondition(key="course_id", match=MatchValue(value=course_id)))
            
            if conditions:
                query_filter = Filter(must=conditions)

        # 3️⃣ Search using Qdrant 1.16.2 API - use query_points method
        search_results = self.client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            limit=k,
            query_filter=query_filter,
            with_payload=True
        ).points

        # 4️⃣ Convert results to LangChain Documents
        documents = []
        for hit in search_results:
            doc = Document(
                page_content=hit.payload.get("text", ""),
                metadata={
                    "score": hit.score,
                    "lecture_id": hit.payload.get("lecture_id"),
                    "user_id": hit.payload.get("user_id"),
                    "course_id": hit.payload.get("course_id"),
                    **{k: v for k, v in hit.payload.items() if k not in ["text", "lecture_id", "user_id", "course_id"]}
                }
            )
            documents.append(doc)

        return documents
    
    def get_collection_info(self, collection_name: str):
        """Get information about a collection"""
        try:
            return self.client.get_collection(collection_name)
        except Exception:
            return None
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")

# Global instance
qdrant_store = QdrantVectorStore()

def save_index(chunks: List[str], lecture_id: str, user_id: int, course_id: int = None):
    """Save text chunks to Qdrant with metadata"""
    collection_name = f"lecture_{lecture_id}"
    
    # Create collection
    qdrant_store.create_collection(collection_name)
    
    # Prepare metadata for chunks
    metadata = []
    for i, chunk in enumerate(chunks):
        chunk_meta = {
            "lecture_id": lecture_id,
            "user_id": user_id,
            "chunk_index": i
        }
        if course_id is not None:
            chunk_meta["course_id"] = course_id
        metadata.append(chunk_meta)
    
    # Add to Qdrant
    qdrant_store.add_texts(collection_name, chunks, metadata)
    
    return collection_name

def load_index(lecture_id: str):
    """Load a lecture collection for searching"""
    collection_name = f"lecture_{lecture_id}"
    return qdrant_store

def search_lectures(
    query: str, 
    lecture_ids: List[str], 
    user_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search across multiple lectures"""
    all_results = []
    
    for lecture_id in lecture_ids:
        collection_name = f"lecture_{lecture_id}"
        
        try:
            # Check if collection exists
            collection_info = qdrant_store.get_collection_info(collection_name)
            if collection_info is None:
                continue
            
            # Search in this lecture
            docs = qdrant_store.similarity_search(
                collection_name=collection_name,
                query=query,
                k=3,  # Get top 3 from each lecture
                user_id=user_id
            )
            
            # Add lecture_id to results
            for doc in docs:
                result = {
                    "lecture_id": lecture_id,
                    "text": doc.page_content,
                    "score": doc.metadata.get("score", 0.0),
                    "metadata": doc.metadata
                }
                all_results.append(result)
                
        except Exception as e:
            print(f"Error searching lecture {lecture_id}: {e}")
            continue
    
    # Sort by score and limit results
    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:limit]
