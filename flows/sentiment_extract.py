from prefect import task
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from prefect_dbt.cli import DbtCoreOperation
from os.path import join
import pandas as pd


def get_sentiment(text, reddit_obj_id, reddit_obj_type):
    
    # Function that uses the SpaCy library to calculate sentiment. Text for each post/comment is analyzed for sentiment and postive and negative words are extracted.

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


def load_submission_data(dir_path: str) -> pd.DataFrame:
    # Load post data from subreddit
    submission_ddf = pd.read_csv(dir_path)
    return submission_ddf

def load_comment_data(dir_path: str) -> pd.DataFrame:
    # Load comment data for each extracted post from subreddit
    comment_ddf = pd.read_csv(dir_path)
    return comment_ddf


@task(name="Process sentiment for subreddit data")
def process_sentiment(dir_path: str):
    # Loads submission and post data, processes sentiment, and then creates a new datframe for the resuting data
    
    sub_ddf = load_submission_data(join(dir_path, "submissions.csv"))
    print(sub_ddf)
    com_ddf = load_comment_data(join(dir_path, "comments.csv"))
    print(com_ddf)
    sub_sent_process = sub_ddf.apply(lambda x: get_sentiment(str(x['submission_text']), x['submission_id'], "submission"), axis=1).tolist()
    com_sent_process = com_ddf.apply(lambda x: get_sentiment(str(x['comment_text']), x['comment_id'], "comment"), axis=1).tolist()
    concat_sent = sub_sent_process + com_sent_process
    df_sentiment = pd.DataFrame(data=concat_sent, columns=['reddit_obj_id', 'reddit_obj_type',
                                                            'sentiment_score', 'sentiment_label',
                                                            'positive_words', 'negative_words'])
    print(df_sentiment)
    df_sentiment.to_csv(join(dir_path, "sentiments.csv"), index=False)
    


   
@task(name="run dbt to transform bigquery tables", log_prints=True)
def run_dbt_transformations(dir_path) -> None:
    # Run the dbt tranformations defined in the 'solana_subreddit_dbt' folder
   dbt_op = DbtCoreOperation(
      commands=["dbt deps", "dbt build"],
      working_dir=dir_path,
      project_dir=dir_path,
      profiles_dir=dir_path
   )
   dbt_op.run()
