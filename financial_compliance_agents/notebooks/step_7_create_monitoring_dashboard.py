# Databricks notebook source
def update_metrics():
    """Update daily metrics"""
    metrics = spark.sql(f"""
        SELECT 
            current_date() as metric_date,
            COUNT(*) as total_queries,
            AVG(response_time) as avg_response_time,
            AVG(rating) as satisfaction_rate
        FROM {catalog_name}.{schema_name}.agent_feedback
        WHERE DATE(timestamp) = current_date()
    """)
    
    metrics.write.mode("append").saveAsTable(
        f"{catalog_name}.{schema_name}.agent_metrics"
    )