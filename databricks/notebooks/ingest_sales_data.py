from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SalesIngestion").getOrCreate()

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

# Read raw CSV from ADLS
raw_path = f"abfss://raw@{storage_account}.dfs.core.windows.net/sales/sales_data.csv"
print(f"Reading from: {raw_path}")

df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(raw_path)

print("Raw data count:", df.count())
df.show()

# Save to processed zone as Delta
processed_path = f"abfss://processed@{storage_account}.dfs.core.windows.net/sales/"

df.write.format("delta") \
    .mode("overwrite") \
    .save(processed_path)

print("Ingestion completed successfully!")
