import pandas as pd
import praw
import time
from prefect import task
from datetime import datetime
from pathlib import Path
from prefect_gcp.cloud_storage import GcsBucket
from output_manager import *



def reddit_client(client_id: str, client_secret: str, reddit_username: str) -> praw.Reddit:
    # Set up PRAW instance
    
    reddit_api = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=reddit_username,
        user_agent=f"python_script:crypto_scraper:v1 (by /u/{reddit_username})",
    )

    return reddit_api

def submission_fetcher(submission, output_manager: OutputManager):
    # Get the submission data
    submission_data_list = (submission.id, submission.author.name, submission.title, 
                            [submission.selftext.replace(',', '')], submission.ups, submission.downs, 
                            datetime.utcfromtimestamp(submission.created_utc), submission.url)                    
    output_manager.submissions_list.append(submission_data_list)

def comments_fetcher(submission, output_manager: OutputManager, reddit_api: praw.Reddit):
    # Get the comments for each post (capped at 200 for posts that have more comments
    try:
        submission_rich_data = reddit_api.submission(id=submission.id)
        if submission_rich_data.num_comments <= 200:
            print(f"Requesting {submission_rich_data.num_comments} comments...")
        else:
            print(f"Requesting 200 comments...")
        comments = submission_rich_data.comments
    except:
        print(f"Submission not found in PRAW: `{submission.id}` - `{submission.title}` - `{submission.full_link}`")
        return
    for comment in comments:
        if comment.author == None:
            author_name = pd.NA
        else:
            author_name =  comment.author.name

        comment_data_list = (submission.id, comment.id, author_name, [comment.body.replace(',', '')], 
                                                        comment.ups, comment.downs, datetime.utcfromtimestamp(comment.created_utc), submission.url)
                                                        
        output_manager.comments_list.append(comment_data_list)


@task(name="Writing subreddit data to gcs bucket")
def write_gcs(path: Path) -> None:
    # Write data to gcs bucket
    gcs_block = GcsBucket.load("crypto-reddit")
    gcs_block.upload_from_folder(from_folder=path, to_folder=path)


@task(name="Fetching Subreddit Data", log_prints=True, retries=3)
def fetch_subreddit_data(client_id: str, client_secret: str, reddit_username: str, num_days: int, output_manager: OutputManager, spark: SparkSession):
    # Gets subreddit and post data that is N days old
    output_manager.reset_lists()

    with reddit_client(client_id, client_secret, reddit_username) as reddit:
        subreddit = reddit.subreddit(output_manager.subreddit)
        new_submissions = subreddit.new(limit=output_manager.subreddit_cap)
        current_time = int(time.time())

        for submission in new_submissions:
            sub_age = (current_time - submission.created_utc) / 60 / 60 / 24
            if sub_age <= num_days:
                submission_fetcher(submission, output_manager)
                comments_fetcher(submission, output_manager, reddit)

    output_manager.store(spark)
