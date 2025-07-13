# Databricks notebook source
# MAGIC %md
# MAGIC ## Step 2 - Prepare Compliance Data
# MAGIC
# MAGIC ### 2.1 Create Delta Tables for Compliance Documents

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Use your existing catalog
# MAGIC USE CATALOG <catalog_name> -- use your catalog;
# MAGIC
# MAGIC -- Create a dedicated schema for the AI agent
# MAGIC CREATE SCHEMA IF NOT EXISTS ai_agents;
# MAGIC USE SCHEMA ai_agents;
# MAGIC
# MAGIC -- Create table for compliance documents
# MAGIC CREATE TABLE IF NOT EXISTS compliance_docs (
# MAGIC     doc_id STRING,
# MAGIC     title STRING,
# MAGIC     content STRING,
# MAGIC     doc_type STRING,
# MAGIC     created_date DATE
# MAGIC ) USING DELTA;

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.2 Set up Python variables & Load Compliance Data

# COMMAND ----------

# Configuration
catalog_name = "dev_1899989130012056"  # Your existing catalog
schema_name = "ai_agents"
table_name = f"{catalog_name}.{schema_name}.compliance_docs"

print(f"Using table: {table_name}")

# COMMAND ----------

### 2.2 Load Sample Compliance Data
from datetime import datetime

# Simplified compliance documents
compliance_data = [
    {
        "doc_id": "KYC001",
        "title": "Know Your Customer Requirements",
        "content": "Banks must verify customer identity including: full name, date of birth, address, and ID. Enhanced checks for high-risk customers.",
        "doc_type": "KYC",
        "created_date": datetime.now().date()
    },
    {
        "doc_id": "AML002",
        "title": "Anti-Money Laundering Rules",
        "content": "Monitor transactions for suspicious patterns. Report transactions over $10,000. Check against sanctions lists.",
        "doc_type": "AML",
        "created_date": datetime.now().date()
    },
    {
        "doc_id": "TRANS003",
        "title": "Transaction Limits",
        "content": "Daily limits: Personal accounts $10,000, Business accounts $50,000. International transfers require additional verification.",
        "doc_type": "Transaction",
        "created_date": datetime.now().date()
    }
]

# Save to table
df = spark.createDataFrame(compliance_data)
df.write.mode("overwrite").saveAsTable(table_name)
print(f"Loaded {df.count()} compliance documents")