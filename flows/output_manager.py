from pyspark.sql import SparkSession
from datetime import datetime
from pyspark.sql import types
from os.path import join

class OutputManager:
    '''Class helps maintain some paths to write files to local machine and bucket'''
    def __init__(self, subreddit: str, subreddit_cap: int, partition_num: int, bucket_dir: str):
        self.submissions_list = []
        self.subreddit = subreddit
        self.subreddit_cap = subreddit_cap
        self.partition_num = partition_num
        self.bucket_dir = bucket_dir
        self.comments_list = []
        self.run_id = datetime.now().strftime("%Y%m%d")

        self.runtime_dir = join(self.subreddit, self.run_id)
        self.bq_upload_dir = join(self.bucket_dir, self.run_id)

        self.submissions_output = join(self.runtime_dir, "submissions")
        self.comments_output = join(self.runtime_dir, "comments")



    def reset_lists(self):
        '''reset lists that have submission and comments data'''
        self.submissions_list = []
        self.comments_list = []

    def store(self, spark: SparkSession):
        '''write post and comment data to local environment'''

        sub_schema = types.StructType([
            types.StructField('submission_id', types.StringType(), True),
            types.StructField('submission_author', types.StringType(), True),
            types.StructField('submission_title', types.StringType(), True),
            types.StructField('submission_text', types.StringType(), True),
            types.StructField('submission_upvotes', types.IntegerType(), True),
            types.StructField('submission_downvotes', types.IntegerType(), True),
            types.StructField('submission_created_time', types.TimestampType(), True),
            types.StructField('submission_url', types.StringType(), True)
        ])

        com_schema = types.StructType([
            types.StructField('submission_id', types.StringType(), True),
            types.StructField('comment_id', types.StringType(), True),
            types.StructField('comment_author', types.StringType(), True),
            types.StructField('comment_text', types.StringType(), True),
            types.StructField('comment_upvotes', types.IntegerType(), True),
            types.StructField('comment_downvotes', types.IntegerType(), True),
            types.StructField('comment_created_time', types.TimestampType(), True),
            types.StructField('comment_url', types.StringType(), True)
        ])

        df_submission = spark.createDataFrame(data=self.submissions_list,schema=sub_schema)
        df_submission = df_submission.repartition(self.partition_num)
        df_submission.write.mode('overwrite').parquet(self.submissions_output)
        df_comment = spark.createDataFrame(data=self.comments_list,schema=com_schema)
        df_comment = df_comment.repartition(self.partition_num)
        df_comment.write.mode('overwrite').parquet(self.comments_output)
