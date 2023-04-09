from prefect import flow
from fetch_subreddit_data import *
from sentiment_extract import *
from output_manager import *
import sys
from prefect_gcp.bigquery import bigquery_load_cloud_storage
from prefect_gcp import GcpCredentials



@flow()
def run_pipeline(client_id: str, client_secret: str, reddit_username: str, bucket_name: str, dbt_dir:str, subreddit: str, subreddit_cap: int, bq_dataset_location: str, num_days: int):
    #  Runs pipeline

    output_manager = OutputManager(subreddit, subreddit_cap)
    fetch_subreddit_data(client_id, client_secret, reddit_username, num_days, output_manager)
    process_sentiment(output_manager.runtime_dir)  
    write_gcs(output_manager.subreddit)  

    gcp_credentials_block = GcpCredentials.load("crypto-gcp-creds")
    
    

    bigquery_load_cloud_storage(
        dataset="solana_subreddit_posts",
        table="submissions",
        uri=f"gs://{bucket_name}/{output_manager.runtime_dir}/submissions.csv",
        gcp_credentials=gcp_credentials_block,
        location=bq_dataset_location
    )

    bigquery_load_cloud_storage(
        dataset="solana_subreddit_posts",
        table="comments",
        uri=f"gs://{bucket_name}/{output_manager.runtime_dir}/comments.csv",
        gcp_credentials=gcp_credentials_block,
        location=bq_dataset_location
    )

    bigquery_load_cloud_storage(
        dataset="solana_subreddit_posts",
        table="sentiments",
        uri=f"gs://{bucket_name}/{output_manager.runtime_dir}/sentiments.csv",
        gcp_credentials=gcp_credentials_block,
        location=bq_dataset_location
    )

    run_dbt_transformations(dbt_dir)

        


if __name__ == '__main__':
   client_id = sys.argv[1]
   client_secret = sys.argv[2]
   reddit_username = sys.argv[3]
   bucket_name = sys.argv[4]
   dbt_dir = sys.argv[5]
   subreddit = sys.argv[6]
   subreddit_cap = sys.argv[7]
   bq_dataset_location = sys.argv[8]
   num_days = sys.argv[9]
   run_pipeline(client_id, client_secret, reddit_username, bucket_name, dbt_dir, subreddit, subreddit_cap, bq_dataset_location, num_days)
