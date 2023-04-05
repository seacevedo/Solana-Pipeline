from prefect import flow
from gcs_bucket_pipeline import *
from gcs_bq_pipeline import *
from multiprocessing import cpu_count
from output_manager import *
from pyspark import SparkConf
from pyspark.sql import SparkSession
import sys

@contextlib.contextmanager
def get_spark_session(conf: SparkConf):
    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    try:
        yield spark
    finally:
        spark.stop()


@flow()
def run_pipeline(client_id: str, client_secret: str, reddit_username: str, bucket_dir: str, dbt_dir:str, subreddit: str, subreddit_cap: int, partition_num: int, num_days: int, gc_project_id: str):

    n_cpus = cpu_count()
    n_executors = n_cpus - 1
    n_cores = 4
    n_max_cores = n_executors * n_cores

    conf = SparkConf().setMaster(f'local[{n_cpus}]').setAppName("solana subreddit scraper")
    conf.set("spark.executor.cores", str(n_cores))
    conf.set("spark.cores.max", str(n_max_cores))

    output_manager = OutputManager(subreddit, subreddit_cap, partition_num, bucket_dir)
    with get_spark_session(conf) as spark_session:
        fetch_subreddit_data(client_id, client_secret, reddit_username, num_days, output_manager, spark_session)
        write_gcs(output_manager.subreddit)
        extract_from_gcs(output_manager.subreddit, output_manager.bucket_dir)
        sub_ddf, com_ddf, sent_ddf = process_sentiment(spark_session, output_manager.bq_upload_dir)  
        migrate_to_bq(sub_ddf, com_ddf, sent_ddf, gc_project_id)
        run_dbt_transformations(dbt_dir)

        


if __name__ == '__main__':
   client_id = sys.argv[1]
   client_secret = sys.argv[2]
   reddit_username = sys.argv[3]
   bucket_dir = sys.argv[4]
   dbt_dir = sys.argv[5]
   subreddit = sys.argv[6]
   subreddit_cap = sys.argv[7]
   partition_num = sys.argv[8]
   num_days = sys.argv[9]
   gc_project_id = sys.argv[10]
   run_pipeline(client_id, client_secret, reddit_username, bucket_dir, dbt_dir, subreddit, subreddit_cap, partition_num, num_days, gc_project_id)
