{{
    config(
        materialized='table',
        unique_key="post_id",
        partition_by={
            "field": "submission_created_time",
            "data_type": "timestamp",
            "granularity": "day"
        },
        cluster_by="sentiment_label"
    )
}}

with sentiment_data as (
    select * 
    from {{ ref("stg_sentiments") }}
    where reddit_obj_type = "submission"
),

submission_data as (
    select *
    from {{ ref("stg_submissions") }}
)

select 
submission_data.post_id,
submission_data.submission_id,
submission_data.submission_author,
submission_data.submission_title,
submission_data.submission_text,
sentiment_data.sentiment_score,
sentiment_data.sentiment_label,
sentiment_data.positive_words,
sentiment_data.negative_words,
submission_data.submission_upvotes,
submission_data.submission_downvotes,
submission_data.submission_created_time,
submission_data.submission_url
from submission_data
left join sentiment_data
on submission_data.submission_id = sentiment_data.reddit_obj_id