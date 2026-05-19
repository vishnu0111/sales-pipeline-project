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
    # Sample test data
    data = [
        (1, "C001", "Laptop", 2, 50000),
        (2, "C002", "Mobile", 1, 20000)
    ]
    columns = ["order_id", "customer_id", "product", "quantity", "price"]

    df = spark.createDataFrame(data, columns)

    # Apply transformation
    df = df.withColumn("total_amount", col("quantity") * col("price"))

    results = df.collect()

    # Assertions
    assert results[0]["total_amount"] == 100000, "Laptop total should be 100000"
    assert results[1]["total_amount"] == 20000,  "Mobile total should be 20000"
    print("test_total_amount_calculation passed!")


def test_customer_kpi_aggregation(spark):
    # Sample test data with same customer buying twice
    data = [
        (1, "C001", "Laptop", 2, 50000),
        (2, "C001", "Mobile", 1, 20000),
        (3, "C002", "Tablet", 3, 15000)
    ]
    columns = ["order_id", "customer_id", "product", "quantity", "price"]

    df = spark.createDataFrame(data, columns)

    # Apply transformation
    df = df.withColumn("total_amount", col("quantity") * col("price"))

    # Aggregate KPI
    customer_kpi = df.groupBy("customer_id") \
        .agg(
            sum("total_amount").alias("total_sales"),
            sum("quantity").alias("total_quantity")
        )

    results = {row["customer_id"]: row for row in customer_kpi.collect()}

    # C001 — 2*50000 + 1*20000 = 120000
    assert results["C001"]["total_sales"] == 120000, "C001 total sales should be 120000"

    # C002 — 3*15000 = 45000
    assert results["C002"]["total_sales"] == 45000,  "C002 total sales should be 45000"

    print("test_customer_kpi_aggregation passed!")


def test_no_null_customer_id(spark):
    # Make sure no null customer ids in data
    data = [
        (1, "C001", "Laptop", 2, 50000),
        (2, "C002", "Mobile", 1, 20000)
    ]
    columns = ["order_id", "customer_id", "product", "quantity", "price"]

    df = spark.createDataFrame(data, columns)

    null_count = df.filter(col("customer_id").isNull()).count()

    assert null_count == 0, "There should be no null customer IDs"
    print("test_no_null_customer_id passed!")