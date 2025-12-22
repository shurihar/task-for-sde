import os

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType

path = os.path.join(os.path.dirname(__file__), 'table.csv')

schema = StructType(
    [
        StructField('id', IntegerType())
    ]
)

spark = SparkSession.builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
spark.read.csv(path, schema=schema, header=True).createOrReplaceTempView('ids')
spark.sql(
    """
        with t1 as (select id, row_number() over(order by id) as rn from ids),
        t2 as (select id, rn, id - rn as diff from t1),
        t3 as (select max(id) + 1 as start_range, min(id) - 1 as end_range from t2 group by diff),
        t4 as (select start_range, end_range, row_number() over(order by start_range) as rn from t3)
        select sr.start_range, er.end_range from t4 sr join t4 er on er.rn = sr.rn + 1
    """
).show()

spark.stop()
