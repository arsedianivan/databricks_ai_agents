# Ensure all dependencies from previous steps are available
catalog_name = "<catalogue_name>" # Replace with your catalog name
schema_name = "ai_agents" # Replace with your schema name
table_name = f"{catalog_name}.{schema_name}.compliance_docs"

# Import required libraries
import openai
import numpy as np
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Get API key
OPENAI_API_KEY = dbutils.secrets.get(scope="ai_agent_secrets", key="openai_api_key")
openai.api_key = OPENAI_API_KEY

# Set up the embedding function
def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=text, model=model)
    return response['data'][0]['embedding']

# Set up the search function
def find_similar_docs(query, k=3):
    query_embedding = np.array(get_embedding(query))
    docs = spark.table(table_name).toPandas()
    
    similarities = []
    for idx, row in docs.iterrows():
        doc_embedding = np.array(row['embedding'])
        similarity = np.dot(query_embedding, doc_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
        )
        similarities.append((similarity, row))
    
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in similarities[:k]]

# Set up the LLM and compliance function
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1, api_key=OPENAI_API_KEY)

compliance_prompt = ChatPromptTemplate.from_template("""
You are a financial compliance assistant. Use the following documents to answer the question.

Documents:
{context}

Question: {question}

Provide a clear, accurate answer based on the documents.
Answer:
""")

def answer_compliance_question(question):
    relevant_docs = find_similar_docs(question, k=2)
    context = "\n\n".join([
        f"Document: {doc['title']}\nContent: {doc['content']}"
        for doc in relevant_docs
    ])
    
    prompt = compliance_prompt.format(context=context, question=question)
    response = llm.predict(prompt)
    
    return {
        "answer": response,
        "sources": [doc['title'] for doc in relevant_docs]
    }

# COMMAND ----------

def chat_with_agent():
    """Simple interactive chat with the compliance agent"""
    print("Financial Compliance AI Agent")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    while True:
        question = input("\nYour question: ")
        if question.lower() == 'exit':
            break
            
        print("\nThinking...")
        result = answer_compliance_question(question)
        
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
        print("-" * 50)

# Run the chat interface
# chat_with_agent()  # Uncomment to run interactive chat

# COMMAND ----------

# Create widgets for Databricks notebook interface
dbutils.widgets.text("question", "What are KYC requirements?", "Ask a compliance question")
dbutils.widgets.dropdown("analysis_type", "Q&A", ["Q&A", "Transaction Check", "Report"], "Analysis Type")

# Get widget values
question = dbutils.widgets.get("question")
analysis_type = dbutils.widgets.get("analysis_type")

# Process based on analysis type
if analysis_type == "Q&A":
    result = answer_compliance_question(question)
    print(f"Question: {question}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSources: {', '.join(result['sources'])}")
    
elif analysis_type == "Transaction Check":
    # Example transaction
    transaction = {
        "amount": 15000,
        "type": "international",
        "customer_type": "personal"
    }
    print(f"Checking transaction: {transaction}")
    result = answer_compliance_question(
        f"Is a ${transaction['amount']} {transaction['type']} transfer allowed for {transaction['customer_type']} accounts?"
    )
    print(f"\nCompliance Check: {result['answer']}")