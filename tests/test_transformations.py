import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local") \
        .appName("TestSales") \
        .getOrCreate()

def test_total_amount_calculation(spark):
    data = [(1, "C001", "Laptop", 2, 50000),
            (2, "C002", "Mobile", 1, 20000)]

    columns = ["order_id", "customer_id", "product", "quantity", "price"]
    df = spark.createDataFrame(data, columns)
    df = df.withColumn("total_amount", col("quantity") * col("price"))

    results = df.collect()
    assert results[0]["total_amount"] == 100000
    assert results[1]["total_amount"] == 20000
    print("Test passed!")