from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, round

spark = SparkSession.builder.appName("SalesTransformation").getOrCreate()

# Read secrets from widgets — passed by Jenkins at runtime
dbutils.widgets.text("AZURE_CLIENT_ID", "")
dbutils.widgets.text("AZURE_CLIENT_SECRET", "")
dbutils.widgets.text("AZURE_TENANT_ID", "")
dbutils.widgets.text("STORAGE_ACCOUNT", "")

client_id       = dbutils.widgets.get("AZURE_CLIENT_ID")
client_secret   = dbutils.widgets.get("AZURE_CLIENT_SECRET")
tenant_id       = dbutils.widgets.get("AZURE_TENANT_ID")
storage_account = dbutils.widgets.get("STORAGE_ACCOUNT")

print(f"Storage Account: {storage_account}")
print("Secrets loaded successfully!")

# Set ADLS Spark config
spark.conf.set(
    f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net",
    "OAuth"
)
spark.conf.set(
    f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net",
    client_id
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net",
    client_secret
)
spark.conf.set(
    f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net",
    f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
)

print("ADLS config set successfully!")

# Read processed delta table
processed_path = f"abfss://processed@{storage_account}.dfs.core.windows.net/sales/"

df = spark.read.format("delta") \
    .load(processed_path)

print("Processed data count:", df.count())
df.show()

# Calculate total amount
df = df.withColumn("total_amount", col("quantity") * col("price"))

# KPI per customer
customer_kpi = df.groupBy("customer_id") \
    .agg(
        sum("total_amount").alias("total_sales"),
        sum("quantity").alias("total_quantity")
    )

customer_kpi = customer_kpi.withColumn("total_sales", round(col("total_sales"), 2))

print("KPI data:")
customer_kpi.show()

# Save to curated zone
curated_path = f"abfss://curated@{storage_account}.dfs.core.windows.net/sales_kpi/"

customer_kpi.write.format("delta") \
    .mode("overwrite") \
    .save(curated_path)

print("Transformation completed successfully!")