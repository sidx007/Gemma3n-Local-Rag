from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from typing import List
class TopicQueryRetriever(BaseRetriever):
    def __init__(self, vector_store, target_topic=None, k=5):
        super().__init__()
        self.vector_store = vector_store
        self.target_topic = target_topic
        self.k = k
    
    def _get_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # Filter by topic if specified
        filter_dict = {"topic": self.target_topic} if self.target_topic else {}
        
        # Get candidates with metadata
        candidates = self.vector_store.similarity_search_with_score(
            query, 
            k=self.k*2,
            filter=filter_dict
        )
        
        # Custom re-ranking logic based on relevant_query metadata
        scored_docs = []
        for doc, similarity_score in candidates:
            # Compare user query with stored relevant_query in metadata
            relevant_query = doc.metadata.get("relevant_query", "")
            # Add your custom scoring logic here
            
            scored_docs.append((doc, similarity_score))
        
        # Sort by your custom scoring and return top k
        return [doc for doc, score in scored_docs[:self.k]]
