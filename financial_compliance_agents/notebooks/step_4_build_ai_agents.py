# Databricks notebook source
# Make sure these are set from previous steps
catalog_name = "<catalog name>" # Replace with your catalog name
schema_name = "ai_agents" # Replace with your schema name
table_name = f"{catalog_name}.{schema_name}.compliance_docs"

# Get OpenAI API key
import openai
OPENAI_API_KEY = dbutils.secrets.get(scope="ai_agent_secrets", key="openai_api_key")
openai.api_key = OPENAI_API_KEY

# Recreate the embedding function
def get_embedding(text, model="text-embedding-ada-002"):
    """Get embedding using OpenAI API"""
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response['data'][0]['embedding']

# Recreate the search function
import numpy as np

def find_similar_docs(query, k=3):
    """Simple vector similarity search"""
    # Generate query embedding
    query_embedding = np.array(get_embedding(query))
    
    # Get all documents
    docs = spark.table(table_name).toPandas()
    
    # Calculate similarities
    similarities = []
    for idx, row in docs.iterrows():
        doc_embedding = np.array(row['embedding'])
        # Cosine similarity
        similarity = np.dot(query_embedding, doc_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
        )
        similarities.append((similarity, row))
    
    # Sort and return top k
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in similarities[:k]]

# COMMAND ----------

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.1,
    api_key=OPENAI_API_KEY
)

# Create compliance prompt template
compliance_prompt = ChatPromptTemplate.from_template("""
You are a financial compliance assistant. Use the following documents to answer the question.

Documents:
{context}

Question: {question}

Provide a clear, accurate answer based on the documents.
Answer:
""")

def answer_compliance_question(question):
    """Answer compliance questions using relevant documents"""
    
    # Find relevant documents
    relevant_docs = find_similar_docs(question, k=2)
    
    # Create context from documents
    context = "\n\n".join([
        f"Document: {doc['title']}\nContent: {doc['content']}"
        for doc in relevant_docs
    ])
    
    # Generate answer
    prompt = compliance_prompt.format(context=context, question=question)
    response = llm.predict(prompt)
    
    return {
        "answer": response,
        "sources": [doc['title'] for doc in relevant_docs]
    }

# Test the agent
test_question = "What are the daily transaction limits?"
result = answer_compliance_question(test_question)
print(f"Question: {test_question}")
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")