<p align="center">
  <img src="https://imgs.search.brave.com/0jB7xKEw6uhG1TGEFvrW9O3oxAWufkZ0Mkqlh271BO8/rs:fit:474:118:1/g:ce/aHR0cHM6Ly9jYW1v/LmdpdGh1YnVzZXJj/b250ZW50LmNvbS9m/ODIzNzY3YjEyYWMw/OGIxNDgyYzY0MjNk/MTRkMGUxNWZhY2E0/NTFmYmQ3NWM4NDcx/MTcwNzY0NDQ1MDI3/NmE2LzY4NzQ3NDcw/NzMzYTJmMmY2OTJl/Njk2ZDY3NzU3MjJl/NjM2ZjZkMmY3NTQy/NTY3YTc5NTgzMzJl/NzA2ZTY3" />
</p>

## Purpose

Solana is a new blockchain protocol that has garrnered interest in the technology space due to its unique proof of history consensus algorithm that results in lightning fast transaction times. However, it has been plagued by numerous outages and scandals, most notably the bankruptcy of FTX, which invested heavily into the Solana ecosystem. Due to this, it would be helpful to keep track of the development and community sentiment around this growing ecosystem. Solana could be useful as a case study to be able to understand what makes a blockchain protocol successful and able to maintain community and developer support. The aim of this project is to build an automated pipeline to gather and synthesize data from community discussion around Solana. Using the [PRAW API](https://praw.readthedocs.io/en/latest/index.html) we will extract posts and comments from the [Solana subreddit](https://www.reddit.com/r/solana/). This data will be transformed and then summarized into a dashboard to extract insight from the discussions of the burgeoning Solana community.


## Questions This Project Seeks to Answer

* Who are the top posters on the subreddit?
* What posts have the most engagement? (Most comments, upvotes, etc.)
* What is the average sentiment over time?
* Do the posts who have the most upvotes always have the most comments?

## Technology Stack


* [PRAW API](https://praw.readthedocs.io/en/latest/index.html) to scrape for posts and associated comments from the Solana subreddit.
* [Google Cloud](https://cloud.google.com/) to upload data to a google cloud bucket and use BigQuery as our data warehouse. We will also set up a VM environment to host our prefect deployment.
* [Terraform](https://www.terraform.io/) for version control of our infrastructure.
* [Prefect](https://www.prefect.io/) will be used to orchestrate and monitor our pipeline. 
* [Pyspark](https://spark.apache.org/) to load data and calculate sentiment quickly and eficiently. Since this is text data, it can take some time to transform data when using Pandas for this dataset. 
* [SpaCy](https://spacy.io/) is an NLP library that we will use to calculate sentiment for both subreddit posts and comments.
* [DBT](https://www.getdbt.com/) to transform out data in BigQuery and prepare it for visualization. 
* [Looker Studio](https://lookerstudio.google.com/overview) to visualize our transformed dataset. 

## Pipeline Architecture
![alt_text](https://github.com/seacevedo/Solana-Pipeline/blob/main/pipeline_infrastructure.png)

* Terraform is used to setup the environment to run our pipeline. When run, the script creates our BigQuery dataset, bucket, and our VM to run our Prefect deployment.
* A Prefect agent is run on our VM compute environment and runs any pending deployments. Using the PRAW API, our flow extracts data from the Solana subreddit and loads it into a GCS bucket. The data from the bucket is extracted and transformed with Pyspark to calculate sentiment for text from both posts and comments. Pyspark is used to speed this process up since Pandas is slower to process this dataset. The data is then uploaded to BigQuery tables for further transformation using DBT. 
* DBT is used to further transform the data by combining the comments and posts data with their corresponding sentiment data. Data aggregations are also made to caluclate the number of comments for each post and calculate upvote/comment ratios.
* Looker studio is used to visualize the fact data tables from the resulting transformations completed by DBT.

## Structure of the Fact Tables

### fact_submission 

| Column        | Data Type   | Description |
| ------------- |:-------------:| -------------:| 
| post_id      | STRING | Surrogate key created using DBT using submission_id and submission_created_time |
| submission_id      | STRING      | Reddit Submission ID|
| submission_author | STRING      |  Author of post |
| submission_title | STRING      | Title of Post |
| submission_text | STRING     | Text of post |
| sentiment_score | NUMERIC      |  Sentiment score of post |
| sentiment_label | STRING      |  Whether the text is postive, negative, or neutral|
| positive_words | STRING     |  postive words found in post|
| negative_words | STRING      |  negative words found in post |
| submission_upvotes | INTEGER     | Number of upvotes post has |
| submission_downvotes | INTEGER      | Nunber of downvotes post has |
| submission_created_time | TIMESTAMP | Time post was created in UTC |
| submission_url | STRING    | URL post links to |

### fact_comment

| Column        | Data Type   | Description |
| ------------- |:-------------:| -------------:| 
| reply_id      | STRING | Surrogate key created using DBT using comment_id and comment_created_time |
| comment_id      | STRING      | Reddit Comment ID|
| submission_id      | STRING      | Reddit Submission ID|
| comment_author | STRING      |  Author of comment |
| comment_text | STRING     | Text of comment |
| sentiment_score | NUMERIC      |  Sentiment score of comment |
| sentiment_label | STRING      |  Whether the text is postive, negative, or neutral|
| positive_words | STRING     |  postive words found in comment|
| negative_words | STRING      |  negative words found in comment |
| comment_upvotes | INTEGER     | Number of upvotes comment has |
| comment_downvotes | INTEGER      | Nunber of downvotes comment has |
| comment_created_time | TIMESTAMP | Time comment was created in UTC |
| comment_url | STRING    | URL comment links to |

### fact_engagement

| Column        | Data Type   | Description |
| ------------- |:-------------:| -------------:| 
| post_id      | STRING | Surrogate key created using DBT using submission_id and submission_created_time |
| submission_id      | STRING      | Reddit Submission ID|
| submission_author | STRING      |  Author of post |
| submission_title | STRING      | Title of Post |
| submission_upvotes | INTEGER     | Number of upvotes post has |
| submission_downvotes | INTEGER      | Nunber of downvotes post has |
| num_comments | INTEGER    | total number of comments the post has |
| upvote_comment_ratio | FLOAT    | ratio of the number of upvotes divided by the number of comments. Metric to measure engagement. |
| submission_created_time | TIMESTAMP | Time post was created in UTC |

### Lineage Graph
![alt_text](https://github.com/seacevedo/Solana-Pipeline/blob/main/lineage_graph.png)

* `staging.submission`, `staging.sentiments`, and `staging.comments` are tables where we have loaded all of our collected subreddit data. 
* `stg_submission`, `stg_sentiments`, and `stg_comments` are views that apply some type casting and create new surrogate keys. This is to ensure that the api does not somehow extract the same id for two different posts.  
* `fact_submission` and `fact_comments` are tables that join the `stg_submission` and `stg_comments` with `stg_sentiments`. They are partitioned by the time of creation and clustered by sentiment label.
* `fact_engagement` is a table that joins the  `fact_submission` and `fact_comments` and applies some aggregations to calculate the number of comments per post and caluclate the upvote comment ratio.





