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
* [Dbt](https://www.getdbt.com/) to transform out data in BigQuery and prepare it for visualization. 
* [Looker Studio](https://lookerstudio.google.com/overview) to visualize our transformed dataset. 




