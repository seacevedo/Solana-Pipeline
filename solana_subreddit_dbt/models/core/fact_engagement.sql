{{ config(materialized='table') }}

with submission_data as (
    select *
    from {{ ref("stg_submissions") }}
),

comment_data_agg as (
    select submission_id, count(1) as num_comments
    from {{ ref("stg_comments") }}
    group by submission_id
)

select 
submission_data.post_id,
submission_data.submission_id,
submission_data.submission_author,
submission_data.submission_title,
submission_data.submission_upvotes,
submission_data.submission_downvotes,
ifnull(comment_data_agg.num_comments, 0) as num_comments,
submission_data.submission_upvotes/nullif(ifnull(comment_data_agg.num_comments, 0), 0) as upvote_comment_ratio,
submission_data.submission_created_time
from submission_data
left join comment_data_agg
on comment_data_agg.submission_id = submission_data.submission_id 
order by submission_data.submission_id
