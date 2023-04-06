import contextlib
import pyspark
from prefect import task
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import types
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from prefect_dbt.cli import DbtCoreOperation
from typing import Tuple
from pyspark.sql import SparkSession
from os.path import join




def get_sentiment(text, reddit_obj_id, reddit_obj_type):
    
    '''
    Function that uses the SpaCy library to calculate sentiment. Text for each post/comment is analyzed for sentiment and postive and negative words are extracted.
    '''

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('spacytextblob')

    doc = nlp(text)
    sent_score = doc._.blob.polarity
    positive_words = []
    negative_words = []
    total_pos = []
    total_neg = []

    if sent_score > 0:
      sent_label = "Positive"
    elif sent_score == 0:
      sent_label = "Neutral"
    else:
      sent_label = "Negative"

    for x in doc._.blob.sentiment_assessments.assessments:
      if x[1] > 0:
        positive_words.append(x[0][0])
      elif x[1] < 0:
        negative_words.append(x[0][0])

    total_pos.append(', '.join(set(positive_words)))
    total_neg.append(', '.join(set(negative_words)))
    
    return [reddit_obj_id, reddit_obj_type, sent_score, sent_label, total_pos, total_neg]


def load_submission_data(spark: SparkSession, dir_path: str) -> SparkDataFrame:
    '''
    Load post data from subreddit
    '''
    submission_ddf = spark.read.parquet(dir_path)
    return submission_ddf

def load_comment_data(spark: SparkSession, dir_path: str) -> SparkDataFrame:
    '''
    Load comment data for each extracted post from subreddit
    '''
    comment_ddf = spark.read.parquet(dir_path)
    return comment_ddf


@task(name="Process sentiment for subreddit data")
def process_sentiment(spark: SparkSession, dir_path: str) ->  Tuple[SparkDataFrame, SparkDataFrame, SparkDataFrame]:\
    '''
    Loads submission and post data, processes sentiment, and then creates a new spark datframe for the resuting data
    '''
    sub_ddf = load_submission_data(spark, join(dir_path, "submissions"))
    sub_ddf.show()
    com_ddf = load_comment_data(spark, join(dir_path, "comments"))
    com_ddf.show()
    sub_sent_process = list(sub_ddf.rdd.map(lambda x: get_sentiment(x.submission_text, x.submission_id, "submission")).collect())
    com_sent_process = list(com_ddf.rdd.map(lambda x: get_sentiment(x.comment_text, x.comment_id, "comment")).collect())
    sent_schema = types.StructType([
            types.StructField('reddit_obj_id', types.StringType(), True),
            types.StructField('reddit_obj_type', types.StringType(), True),
            types.StructField('sentiment_score', types.DoubleType(), True),
            types.StructField('sentiment_label', types.StringType(), True),
            types.StructField('positive_words', types.StringType(), True),
            types.StructField('negative_words', types.StringType(), True)
    ])
    concat_sent = sub_sent_process + com_sent_process
    df_sentiment = spark.createDataFrame(data=concat_sent, schema=sent_schema)
    return sub_ddf, com_ddf, df_sentiment



@task(name="Create bq tables from subreddit data")
def migrate_to_bq(sub_ddf: SparkDataFrame, com_ddf: SparkDataFrame, sent_ddf: SparkDataFrame, gc_project_id: str) -> None:
    '''
    Converts spark dataframes to pandas dataframes and uploads them to BiqQuery as tables
    '''

    gcp_credentials_block = GcpCredentials.load("crypto-gcp-creds")

    sub_ddf.toPandas().to_gbq(
        destination_table="solana_subreddit_posts.submissions",
        project_id=gc_project_id,
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )

    com_ddf.toPandas().to_gbq(
        destination_table="solana_subreddit_posts.comments",
        project_id=gc_project_id,
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )


    sent_ddf.toPandas().to_gbq(
        destination_table="solana_subreddit_posts.sentiments",
        project_id=gc_project_id,
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )
   
@task(name="run dbt to transform bigquery tables", log_prints=True)
def run_dbt_transformations(dir_path) -> None:\
    '''
    Run the dbt tranformations defined in the 'solana_subreddit_dbt' folder
    '''
   dbt_op = DbtCoreOperation(
      commands=["dbt deps", "dbt build --var 'is_test_run: false'"],
      working_dir=dir_path,
      project_dir=dir_path,
      profiles_dir=dir_path
   )
   dbt_op.run()


@task(name="Extract subreddit data from gcs bucket")
def extract_from_gcs(bucket_dir: str, target_dir: str) -> None:
    '''
    Extract the data from the gcs bucket
    '''
    gcs_block = GcsBucket.load("crypto-reddit")
    gcs_block.download_folder_to_path(from_folder=bucket_dir, to_folder=target_dir)
