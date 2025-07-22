from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

def contextual_query(query, context):
    llm = OllamaLLM(model="gemma3n:e2b", streaming=True)  
    
    # Format the prompt directly
    rag_query = f"""
Based ONLY on the provided context, answer the following question. If the information is not present in the context, respond with "I don't have enough information in the provided context to answer this question."

Context Type: {context}

Rules:
1. Use ONLY information from the provided context
2. Quote specific sections when possible
3. If uncertain, acknowledge the limitation
4. Do not add external knowledge or assumptions
5. If the context is incomplete, state what's missing

Question: {query}

Answer based strictly on the context:"""
    
    # Stream directly from LLM
    for chunk in llm.stream(rag_query):
        yield chunk

def query_model(query):
    llm = OllamaLLM(model="gemma3n:e2b", streaming=True)
    
    # Stream directly from LLM without chain
    for chunk in llm.stream(query):
        yield chunk

def main():
    import sys
    for i in query_model("Who is the president of the USA? and what are reasoning algos"):
        print(i, end='', flush=True)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
