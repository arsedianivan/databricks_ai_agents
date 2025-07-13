# Make sure these variables are set from Step 2.1
catalog_name = "<Put your catalog name>"  # Your existing catalog
schema_name = "ai_agents" # Your existing schema
table_name = f"{catalog_name}.{schema_name}.compliance_docs"

# Verify the table exists
try:
    spark.table(table_name).show(5)
    print(f"Table {table_name} found successfully")
except:
    print(f"Table {table_name} not found. Please run Step 2 first.")

# COMMAND ----------

# Option 1: Use OpenAI embeddings (simpler and more reliable)
import openai
import pandas as pd
import numpy as np

# Get the API key from Databricks secrets
OPENAI_API_KEY = dbutils.secrets.get(scope="ai_agent_secrets", key="openai_api_key")
openai.api_key = OPENAI_API_KEY

def get_embedding(text, model="text-embedding-ada-002"):
    """Get embedding using OpenAI API"""
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response['data'][0]['embedding']

# Read documents
docs_df = spark.table(table_name).toPandas()

# Generate embeddings
print("Generating embeddings...")
docs_df['embedding'] = docs_df['content'].apply(lambda x: get_embedding(x))

# Save back with embeddings - need to overwrite schema to add embedding column
spark.createDataFrame(docs_df) \
    .write \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)
print("Embeddings created successfully")

# Verify embeddings were saved
spark.sql(f"SELECT doc_id, title, size(embedding) as embedding_size FROM {table_name}").show()

# COMMAND ----------

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

# Test the search
test_results = find_similar_docs("What are transaction limits?", k=2)
print("Search test results:")
for doc in test_results:
    print(f"- {doc['title']}")