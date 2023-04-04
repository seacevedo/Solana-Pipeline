
{{ config(materialized='view') }}

select
    
    {{ dbt_utils.generate_surrogate_key(['submission_id', 'submission_created_time']) }} as post_id,
    submission_id,
    submission_author,
    submission_title,
    translate(submission_text, "[]", "") as submission_text,
    cast(submission_upvotes as integer) as submission_upvotes,
    cast(submission_downvotes as integer) as submission_downvotes,
    cast(submission_created_time as timestamp) as submission_created_time,
    submission_url


from {{ source('staging','submissions') }}
