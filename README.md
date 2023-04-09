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
* [SpaCy](https://spacy.io/) is an NLP library that we will use to calculate sentiment for both subreddit posts and comments.
* [DBT](https://www.getdbt.com/) to transform out data in BigQuery and prepare it for visualization. 
* [Looker Studio](https://lookerstudio.google.com/overview) to visualize our transformed dataset. 
* [Pandas](https://pandas.pydata.org/) to import and transform our dataset. 

## Pipeline Architecture
![alt_text](https://github.com/seacevedo/Solana-Pipeline/blob/main/pipeline_infrastructure.png)

* Terraform is used to setup the environment to run our pipeline. When run, the script creates our BigQuery dataset, bucket, and our VM to run our Prefect deployment.
* A Prefect agent is run on our VM compute environment and runs any pending deployments. Using the PRAW API, our flow extracts data from the Solana subreddit, calculates the sentiment of the text data and loads it into a GCS bucket. The data from the bucket is then uploaded to BigQuery tables for further transformation using DBT. 
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


## Dashboard Preview
Access the dashboard [here](https://lookerstudio.google.com/reporting/155051d4-8969-4104-b3c3-32b8018f5825/page/6EmLD) 

![alt_text](https://github.com/seacevedo/Solana-Pipeline/blob/main/dashboard_preview.png)

## Replication Steps

### Create a Reddit Account

1. You must create a reddit account in order to be able to scrape subreddit data. 
2. Once you have an account go [here](https://www.reddit.com/prefs/apps). Click on the `create another app...` button at the bottom of the page. Fill in the required fields and select `web app`. Click on `create app`
3. Under the `web_app` text under your newly created app information you should have an id for your application. Record this and the secret key. You will need to parameterize your flow with these tokens in order to use the PRAW apiSetup Google Cloud 

### Setup Google Cloud 

1. Create a google cloud account
2. Setup a new google cloud [project](https://cloud.google.com/).
3. Create a new service account. Give the service account the `Compute Admin`, `Service Account User`, `Storage Admin`, `Storage Object Admin`, and `BigQuery Admin` Roles.
4. After the service account has been created, click on `Manage Keys` under the `Actions` Menu. Click on the `Add Key` dropdown and click on `Create new key`. A prompt should pop up asking to download it as a json or P12 file. Choose the json format and click `Create`. Save your key file.
5. Install the the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk). Assuming you have an Ubuntu linux distro or similar as your environment, follow the directions for `Debian/Ubuntu`. Make sure you log in by running `gcloud init`. Choose the cloud project you created to use.
6. Set the environment variable to point to your downloaded service account keys json file:

`export GOOGLE_APPLICATION_CREDENTIALS=<path/to/your/service-account-authkeys>.json`

7. Refresh token/session, and verify authentication
`gcloud auth application-default login`

8. Make sure these APIs are enabled for your project:

https://console.cloud.google.com/apis/library/iam.googleapis.com
https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com
https://console.cloud.google.com/apis/library/compute.googleapis.com

### Setup VM Environment

1. Clone the repo and `cd` into the `Solana-Pipeline` folder
2. Install [Terraform](https://www.terraform.io/)
3. Make sure you have an SSH key generated to log into the VM.
4. `cd` to the `terraform` directory and enter the commands `terraform init`, `terraform plan`, and `terraform apply`. You can remove the corresponding infrastructure by using `terraform destroy`. For the plan and destroy commands you will be prompted to input the following variables:

| Variable       | Description  |
| ------------- |:-------------:|
| GOOGLE_CLOUD_PROJECT_ID      | ID of the google cloud project | 
| SERVICE_ACCOUNT_EMAIL     | Email of the service account you used to generate the key file  | 
| SSH_USER | Username you used for the SSH Key   |  
| SSH_PUBLIC_KEY_PATH | Path to the public SSH key      |
| SETUP_SCRIPT_PATH | Path of the setup.sh script within the Solana-Pipeline directory     | 
| SERVICE_ACCOUNT_FILE_PATH | Keyfile of the service account   | 
| GOOGLE_CLOUD_BUCKET_NAME | Name of your GCS bucket   | 

5. Log in your newly created VM environment using the following command `ssh -i /path/to/private/ssh/key username@vm_external_ip_address`. As an alternative, follow this [video](https://www.youtube.com/watch?v=ae-CV2KfoN0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) to help setup SSH in a VS code environment, which allows for port forwarding from your cloud VM to your local machine. Type the command `cd /Solana-Pipeline` to `cd` into the `/Solana-Pipeline` directory. 
6. Activate the newly created python virtual environment using the command: `source solana-pipeline-env/bin/activate` (You may have to wait a few minutes in order for the vm instance to finish running the setup.sh script and installing all necessary dependancies).
7. Make sure you update the profiles.yml and schema.yml files in your dbt directory. Change the appropriate fields with the correct google cloud project id, dataset name, location, and keyfile path. 
8. You should now have prefect installed. Run the prefect server locally using the `prefect orion start` command to monitor flows. This is needed to access the Orion UI. In another terminal, `cd` into the `flows` directory and run the command `prefect deployment build main_flow.py:run_pipeline -n "solana-pipeline-deployment" --cron "0 0 * * *" -a` to build the prefect deployment that runs at 12:00 AM every day. Make sure you setup the following prefect blocks before running:

| Block Name       | Description  |
| ------------- |:-------------:|
| crypto-gcp-creds      | Block pertaining to your Google cloud credentials. You need the JSON keyfile you downloaded earlier to set it up | 
| crypto-reddit   | Block pertaining to the bucket you wish to load the data into | 

  
9. You can then run the deployment using the command `prefect deployment run run-pipeline/solana-pipeline-deployment --params '{"client_id":<client_id>, "client_secret":<client_secret>, "reddit_username":<reddit_username>, "bucket_name":"solana_reddit", "dbt_dir":"/root/Solana-Pipeline/solana_subreddit_dbt/", "subreddit":"solana", "subreddit_cap":100, "bq_dataset_location":"us-central1", "num_days":15}'` as an example. The deployment should be scheduled.
10. Your newly scheduled deployment can be run when initiating a prefect agent. Run the command `prefect agent start -q "default"` to run your deployment.

## Next Steps
* Add CI/CD tooling to automate the workflow and make it more production ready
* Take advantage of systemd to run the agent when the VM starts up
* Add Piperider to allow for data profiling and monitoring
* Add docker containers to aid with reproducibility of the presented pipeline.

