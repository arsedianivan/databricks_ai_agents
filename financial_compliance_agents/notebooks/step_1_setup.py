# Databricks notebook source
# MAGIC %md
# MAGIC ## Step 1.4 - Install Required Libraries

# COMMAND ----------

# MAGIC %pip install langchain openai faiss-cpu sentence-transformers pandas numpy
# MAGIC %pip install databricks-vectorsearch databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1.5 - Set up Authentication 

# COMMAND ----------

import os
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

# Set up API keys (store securely in Databricks secrets)
OPENAI_API_KEY = dbutils.secrets.get(scope="ai_agent_secrets", key="openai_api_key")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# COMMAND ----------

# List available scopes (won't show secret values)
dbutils.secrets.listScopes()

# List keys in a scope (won't show values)
dbutils.secrets.list("ai_agent_secrets")

# Use secrets in code (values are redacted in output)
api_key = dbutils.secrets.get(scope="ai_agent_secrets", key="openai_api_key")
print(f"API Key retrieved: {api_key}")  # Will show [REDACTED]