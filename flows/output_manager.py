from datetime import datetime
import pandas as pd
from os.path import join, exists
import os


class OutputManager:
    # Class helps maintain some paths to write files to local machine and bucket
    def __init__(self, subreddit: str, subreddit_cap: int):
        self.submissions_list = []
        self.subreddit = subreddit
        self.subreddit_cap = subreddit_cap
        self.comments_list = []
        self.run_id = datetime.now().strftime("%Y%m%d")

        self.runtime_dir = join(self.subreddit, self.run_id)

        self.submissions_output = join(self.runtime_dir, "submissions.csv")
        self.comments_output = join(self.runtime_dir, "comments.csv")



    def reset_lists(self):
        # reset lists that have submission and comments data
        self.submissions_list = []
        self.comments_list = []

    def store(self):
        # write post and comment data to local environment
        if exists(self.runtime_dir) == False:
            os.makedirs(self.runtime_dir)
        df_submission = pd.DataFrame(data=self.submissions_list,columns=['submission_id', 'submission_author', 
                                                                         'submission_title', 'submission_text', 
                                                                         'submission_upvotes', 'submission_downvotes',
                                                                         'submission_created_time', 'submission_url'])
        df_submission.to_csv(self.submissions_output, index=False)
        df_comment = pd.DataFrame(data=self.comments_list,columns=['submission_id', 'comment_id',
                                                                   'comment_author', 'comment_text', 
                                                                   'comment_upvotes', 'comment_downvotes',
                                                                   'comment_created_time', 'comment_url'])
        df_comment.to_csv(self.comments_output, index=False)
