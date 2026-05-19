import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, round

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .master("local") \
        .appName("TestSales") \
        .getOrCreate()

def test_total_amount_calculation(spark):
    data = [
        (1, "C001", "Laptop", 2, 50000),
        (2, "C002", "Mobile", 1, 20000)
    ]
    columns = ["order_id", "customer_id", "product", "quantity", "price"]
    df = spark.createDataFrame(data, columns)
    df = df.withColumn("total_amount", col("quantity") * col("price"))
    results = df.collect()
    assert results[0]["total_amount"] == 100000
    assert results[1]["total_amount"] == 20000
    print("test_total_amount_calculation passed!")

def test_customer_kpi_aggregation(spark):
    data = [
        (1, "C001", "Laptop", 2, 50000),
        (2, "C001", "Mobile", 1, 20000),
        (3, "C002", "Tablet", 3, 15000)
    ]
    columns = ["order_id", "customer_id", "product", "quantity", "price"]
    df = spark.createDataFrame(data, columns)
    df = df.withColumn("total_amount", col("quantity") * col("price"))
    customer_kpi = df.groupBy("customer_id") \
        .agg(
            sum("total_amount").alias("total_sales"),
            sum("quantity").alias("total_quantity")
        )
    results = {row["customer_id"]: row for row in customer_kpi.collect()}
    assert results["C001"]["total_sales"] == 120000
    assert results["C002"]["total_sales"] == 45000
    print("test_customer_kpi_aggregation passed!")

def test_no_null_customer_id(spark):
    data = [
        (1, "C001", "Laptop", 2, 50000),
        (2, "C002", "Mobile", 1, 20000)
    ]
    columns = ["order_id", "customer_id", "product", "quantity", "price"]
    df = spark.createDataFrame(data, columns)
    null_count = df.filter(col("customer_id").isNull()).count()
    assert null_count == 0
    print("test_no_null_customer_id passed!")