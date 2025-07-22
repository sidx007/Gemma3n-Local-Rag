import sys
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.llms.base import LLM
from time import perf_counter as timer
from typing import Generator, List, Optional, Any
from misc.gemma3 import GoogleGeminiClient
import os
import nltk, numpy as np
from llama_cpp import Llama
class LangChainRAG:
    def __init__(self, files: List[str], chunk_size: int = 1000, chunk_overlap: int = 100, topic: str = None, add_metadata: bool = True, gemini_api_key: Optional[str] = None, llm: LLM = None,details:str=None):
        """ Initialize the RAG system with PDF files and parameters."""
        self.files = [f for f in files if f.lower().endswith('.pdf')]
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = []
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None
        self.topic = topic
        self.add_metadata = add_metadata
        self.gemini_api_key = gemini_api_key
        self.details = details
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="C:\\models\\static-mrl"
        )
        
        model_path = "C:\\Users\\User\\Desktop\\LLM\\Rag\\models\\gemma3n-e2b.gguf"
        self.prompt_tokens = 2048
        self.llm = Llama(
            model_path=model_path,
            n_ctx=self.prompt_tokens,  # Context window size
            n_threads=4,  # Number of threads to use
            verbose=False
    )
        #self.positive = self.json_file_to_list('data/oos_test.json') + self.json_file_to_list('data/oos_train.json')
        #self.positive = [item[0] for item in self.positive]
        #self.positive_embeddings = np.array(self.embeddings.embed_documents(self.positive))
        # Initialize custom LLM
        
        if not self.files:
            print("No PDF files provided.")
        else:
            self._load_and_process_documents(existing=os.path.exists("./" + self.topic))
    def contextual_query(self, query: str, context: str) -> Generator[str, None, None]:
        rag_query = f"""
Based ONLY on the provided context, answer the following question. If the context does not provide enough information, acknowledge the limitation and reply with all you know about the query."

Context Type: {context}

Rules:
1. Quote specific sections when possible
2. If uncertain, acknowledge the limitation and answer based on your own knowledge
3. Do not add external knowledge without telling about it
4. If the context is incomplete, state what's missing and give the answer stating what should be the answer according to your knowledge
5. Do not let any question remain unanswered
Question: {query}

Answer based strictly on the context:"""
        max_new = 8192 - self.prompt_tokens
        max_new = min(max_new, 4096)   
        # Stream directly from LLM
        for chunk in self.llm(
            rag_query,
            max_tokens=max_new,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stream=True,
            stop=["</s>", "<end_of_turn>"]
        ):
            if 'choices' in chunk and len(chunk['choices']) > 0:
                token = chunk['choices'][0]['text']
                if token:
                    yield token

    def json_file_to_list(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def format_chat_prompt(self, user_message: str, system_message: str = None) -> str:
        """Format the input using Gemma-compatible chat template."""
        if system_message:
            return f"""<start_of_turn>user
    {system_message}

    {user_message}<end_of_turn>
    <start_of_turn>model
    """
        else:
            return f"""<start_of_turn>user
    {user_message}<end_of_turn>
    <start_of_turn>model
    """ 
    def query_model(self,prompt: str):
        max_gen = 8192 - self.prompt_tokens 
        """Stream the answer back token-by-token with proper chat formatting."""
        # Format the prompt using chat template
        formatted_prompt = self.format_chat_prompt(prompt,"You are a helpful assistant and you will only reply in concise and limited words, reply in depth only if asked by the user")
        for chunk in self.llm(
            formatted_prompt,
            max_tokens=max_gen,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stream=True,
            stop=["</s>", "<end_of_turn>"]
        ):
            tok = chunk["choices"][0]["text"]
            if tok is not None and tok != "":
                yield str(tok)
    def cosine_similarity(self,vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return dot_product / (norm_vec1 * norm_vec2)
    def predict(self,query: str, threshold: float=0.026198) -> bool:
        query_embedding = self.embeddings.embed_query(query)
        
        positive_similarities = []
        for pos_emb in self.positive_embeddings:
            sim = self.cosine_similarity(query_embedding, pos_emb)
            positive_similarities.append(sim)
        
        avg_positive_similarity = np.mean(positive_similarities)
        
        similarity = avg_positive_similarity
        return similarity > threshold
    def _split_with_metadata(self):
        """Split documents with metadata preservation"""
        print("Splitting documents with metadata preservation...")
        
        if not self.documents:
            raise ValueError("No documents to process. Check if PDF files were loaded correctly.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
        chunks = []
        for doc in self.documents:
            # Split the document
            doc_chunks = text_splitter.split_documents([doc])
            
            if self.add_metadata:
                gemini = GoogleGeminiClient(self.gemini_api_key)
                topic_prompt = f"""
                        For the following Document, give it a suitably descriptive topic label.\
                        The topic label will be used for categorization and retrieval purposes.\
                        Document content: 
                        """
                find_relevant_query_prompt = f"""
                        For the following Document, find the most relevant query that could be used to retrieve it.
                        Document content:
                    """
                for i,doc in enumerate(doc_chunks):
                    print(f"Processing chunk {i+1}/{len(doc_chunks)}")
                    doc.metadata['topic'] = gemini.generate(topic_prompt + doc.page_content).strip()
                    doc.metadata['relevant_query'] = gemini.generate(find_relevant_query_prompt + doc.page_content).strip()
            chunks.extend(doc_chunks)
        
            print(f"Created {len(chunks)} chunks with metadata")
            
            # Create vector store with metadata
            self.vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 8 }
            )
    
    def _load_and_process_documents(self, existing: bool = False):
        """Load and process PDF documents using LangChain"""
        print("Loading PDF documents...")
        if existing:
            print(f"Loading existing documents from ./projects/{self.topic}")
            self.vector_store = FAISS.load_local(
                "./projects/"+self.topic, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print(f"Processing new documents from: {self.files}")
            # FIX: Actually populate self.documents
            for pdf_path in self.files:
                try:
                    loader = PyPDFLoader(pdf_path)
                    docs = loader.load()
                    self.documents.extend(docs)  # Add this line!
                    print(f"Loaded {len(docs)} pages from {pdf_path}")
                except Exception as e:
                    print(f"Error loading {pdf_path}: {e}")
            
            if not self.documents:
                print("No documents were loaded successfully.")
                return
                
            self._split_with_metadata()
            
            # Ensure projects directory exists
            projects_dir = "./projects"
            os.makedirs(projects_dir, exist_ok=True)
            
            # Save to projects folder
            self.vector_store.save_local(f"./projects/{self.topic}")
            print("Vector store created and saved locally.")
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 20,
                "lambda_mult": 0.5
            }
        )
        print("RAG setup complete!")


    def extract_keywords_directly(self,query, num_keywords=5):
        """Extract keywords directly from user query"""
        
        keyword_prompt = f"""
        Extract the {num_keywords} most important keywords from this query for document retrieval
        including the terms which might have different or similar meanings and can improve retrieval from a document:
        
        Query: {query}
        
        Focus on:
        - Main concepts
        - Technical terms
        - Key entities
        - Search-relevant terms
        Directly reply wit keywords and nothing else
        Keywords (comma-separated):
        """
        output = ""
        response = self.query_model(keyword_prompt)
        for chunk in response:
            output += chunk
        keywords = [kw.strip() for kw in output.split(',')]
        return keywords

    def add_keywords_to_query(self, query: str, keywords: List[str]) -> str:
        """Add extracted keywords to the query"""
        if not keywords:
            return query
        
        keyword_str = ", ".join(keywords)
        enhanced_query = f"{query} (Keywords: {keyword_str})"
        return enhanced_query

    def extractive_summary(self, query: str, text: str, num_sentences: int = 3) -> str:
        """Generate an extractive summary of the text using existing embedding model"""
        if not text:
            return ""   
        
        # Simple sentence splitting (alternative to nltk)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return text
        
        # Encode sentences using the existing HuggingFace embeddings
        sentence_embeddings = self.embeddings.embed_documents(sentences)
        query_embedding = self.embeddings.embed_query(query)
        
        # Convert to numpy arrays for similarity computation
        sentence_embeddings = np.array(sentence_embeddings)
        query_embedding = np.array(query_embedding)
        
        # Compute cosine similarity between query and each sentence
        similarities = []
        for sent_emb in sentence_embeddings:
            # Compute cosine similarity
            dot_product = np.dot(query_embedding, sent_emb)
            norm_query = np.linalg.norm(query_embedding)
            norm_sent = np.linalg.norm(sent_emb)
            similarity = dot_product / (norm_query * norm_sent) if (norm_query * norm_sent) > 0 else 0
            similarities.append(similarity)
        
        # Get top N sentences based on similarity
        top_indices = np.argsort(similarities)[-num_sentences:]
        summary_sentences = [sentences[i] for i in sorted(top_indices)]
        
        return ' '.join(summary_sentences)

    def query(self, question: str):
        """Query the RAG system"""
        #print(f"Received query: {question}")
        #question = self.add_keywords_to_query(question, self.extract_keywords_directly(question))
        #print(f"Enhanced query: {question}")
        if not self.retriever:
            return "No documents loaded. Please check your PDF files."
        
        print(f"Searching for relevant context...")
        start_time = timer()
        
        # Retrieve relevant documents
        relevant_docs = self.retriever.get_relevant_documents(question)
        
        end_time = timer()
        print(f"Time taken: {end_time-start_time:.5f} seconds.")
        print(f"Found {len(relevant_docs)} relevant chunks")
        
        question_embedding = self.embeddings.embed_query(question)
        # Build context from retrieved documents
        context = ""
        cosine = 0
        for doc in relevant_docs:
            doc_embedding = self.embeddings.embed_query(doc.page_content)
            cosine += self.cosine_similarity(question_embedding, doc_embedding)
            context += self.extractive_summary(question, doc.page_content) + " "
        
        # Generate response using your custom contextual_query function
        print("Generating response...")
        print(cosine/len(relevant_docs))
        if cosine/len(relevant_docs) < 0.15:
            # Use general knowledge - yield tokens one by one
            for chunk in self.query_model(question):
                yield chunk
        else:
            # Use contextual query with document context - yield tokens one by one
            for chunk in self.contextual_query(question, context):
                yield chunk
    def check_query(self, query: str) -> bool:
        response = self.query_model("""
        Check Whether a document about"""+self.details+"""
        Can answer the following query"""+query+"""
        Reply 0 if:
         - The document might containt some context about what is asked in the query
         - You might build up on your knowledge by having the context specifically from the document and give a better reply
        Reply 1 if:
         - The document contains completely irrelevant information as to what is asked in the query
         - You can easily reply to the general query without using the document
        Reply only in 0 or 1.
""")    
        output = ""
        for i in response:
            output += i.strip()
        print(output)
        return output.strip()=='1'
        
    def interactive_query(self):
        """Interactive query loop"""
        if not self.retriever:
            print("No documents loaded. Please check your PDF files.")
            return
        
        print("RAG system ready! Type 'exit' to quit.")
        
        while True:
            prompt = str(input("User: "))
            if prompt.lower() == 'exit':
                break
            
            if not prompt.strip():
                continue

            try:
                if 1==2:
                    response = self.query_model(prompt)
                    for chunk in response:
                        print(chunk, end='', flush=True)
                        sys.stdout.flush()
                    print()
                    continue
                response = self.query(prompt)
                for chunk in response:
                    print(chunk, end='', flush=True)
                    sys.stdout.flush()
            except Exception as e:
                print(f"Error processing query: {e}")


def main():
    files = ['C:\\Users\\User\\Desktop\\LLM\\Rag\\p2.pdf']
    topic = input("Enter the topic for RAG system: ")
    #details = input("What is the document about?")
    add_metadata = input("Do you want to add metadata to the documents? (yes/no): ").strip().lower() == 'yes'
    gemini_api_key = None
    if add_metadata:
        gemini_api_key = input("Enter your Google Gemini API key: ").strip()
    rag = LangChainRAG(files, chunk_size=800, chunk_overlap=100, topic=topic, add_metadata=add_metadata, gemini_api_key=gemini_api_key)
    print("RAG system initialized. Type 'exit' to quit.")
    print("You can now ask questions related to the content of the PDF documents.")
    try:
        response = rag.query("How is safe proxy used in google?")
        for chunk in response:
            print(chunk, end='', flush=True)
            sys.stdout.flush()
    except Exception as e:
        print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()