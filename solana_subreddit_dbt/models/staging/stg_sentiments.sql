{{ config(materialized='view') }}

select
    
    {{ dbt_utils.generate_surrogate_key(['reddit_obj_id', 'sentiment_score']) }} as sentiment_id,
    reddit_obj_id,
    reddit_obj_type,
    cast(sentiment_score as numeric) as sentiment_score,
    sentiment_label,
    translate(positive_words, "[]", "") as positive_words,
    translate(negative_words, "[]", "") as negative_words


from {{ source('staging','sentiments') }}