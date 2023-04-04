from prefect import flow
from gcs_bucket_pipeline import *
from gcs_bq_pipeline import *
from multiprocessing import cpu_count
from output_manager import *
from pyspark import SparkConf
from pyspark.sql import SparkSession

@contextlib.contextmanager
def get_spark_session(conf: SparkConf):
    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    try:
        yield spark
    finally:
        spark.stop()


@flow()
def run_pipeline(client_id: str, client_secret: str, reddit_username: str, bucket_dir: str, dbt_dir:str, subreddit: str, subreddit_cap: int, partition_num: int, num_days: int):

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
        migrate_to_bq(sub_ddf, com_ddf, sent_ddf)
        run_dbt_transformations(dbt_dir)

        
        


if __name__ == '__main__':
    run_pipeline(client_id, client_secret,  reddit_username, bucket_dir, dbt_dir, subreddit, 50, 10, 1)
