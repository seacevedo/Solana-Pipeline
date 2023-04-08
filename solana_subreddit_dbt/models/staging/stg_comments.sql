{{ config(materialized='view') }}

select
    
    {{ dbt_utils.generate_surrogate_key(['comment_id', 'comment_created_time']) }} as reply_id,
    submission_id,
    comment_id,
    comment_author,
    translate(comment_text, "[]'", "") as comment_text,
    cast(comment_upvotes as integer) as comment_upvotes,
    cast(comment_downvotes as integer) as comment_downvotes,
    cast(comment_created_time as timestamp) as comment_created_time,
    comment_url


from {{ source('staging','comments') }}
