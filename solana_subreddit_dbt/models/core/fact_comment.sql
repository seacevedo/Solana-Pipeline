{{
    config(
        materialized='table',
        unique_key="reply_id",
        partition_by={
            "field": "comment_created_time",
            "data_type": "timestamp",
            "granularity": "day"
        },
        cluster_by="sentiment_label"
    )
}}

with sentiment_data as (
    select * 
    from {{ ref("stg_sentiments") }}
    where reddit_obj_type = "comment"
),

comment_data as (
    select *
    from {{ ref("stg_comments") }}
)

select 
comment_data.reply_id,
comment_data.comment_id,
comment_data.submission_id,
comment_data.comment_author,
comment_data.comment_text,
sentiment_data.sentiment_score,
sentiment_data.sentiment_label,
sentiment_data.positive_words,
sentiment_data.negative_words,
comment_data.comment_upvotes,
comment_data.comment_downvotes,
comment_data.comment_created_time,
comment_data.comment_url
from comment_data
left join sentiment_data
on comment_data.comment_id = sentiment_data.reddit_obj_id