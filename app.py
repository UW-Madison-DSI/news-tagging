import logging

import streamlit as st
from cachetools import TTLCache, cached

from data_loader import Post, download_posts, load_posts, get_all_tags, filter_posts
from gpt import tag


@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_posts() -> list[Post]:
    """Update and get all posts."""

    existing_posts = load_posts()
    live_posts = download_posts()
    exist_ids = [p.id for p in existing_posts]

    # Filter out posts that are already exist
    new_posts = [post for post in live_posts if post.id not in exist_ids]

    # Tag and save new posts
    for post in new_posts:
        logging.info(f"Tagging new post {post.id}")
        post.tags_gpt = tag(post.title, post.content)
        post.save()

    existing_posts.extend(new_posts)
    return existing_posts


st.set_page_config(page_title="UW News tagging", page_icon="📰", layout="wide")
st.title("UW News tagging (prototype)")

"""
This demo compares the original tags from UW News articles, 
sourced from the [news feed](https://news.wisc.edu/feed), 
with tags that are generated by GPT-4. These newly generated tags are 
derived from both the title and the complete content of each article.

[Core prompt engineering code](https://github.com/UW-Madison-DSI/news-tagging/blob/00d2a7d5f5a95ea80549664040648db5f4743e69/gpt.py#L12C1-L27C6)
"""

st.header("📰 UW News articles")
st.session_state.filter_selection = None

posts = get_posts()
tags = get_all_tags(posts)

with st.expander("🏷️ Filter articles by Tags"):
    # Show tags in a grid
    N_TAGS_PER_ROW = 5
    for i in range(0, len(tags), N_TAGS_PER_ROW):
        row_tags = tags[i : i + N_TAGS_PER_ROW]

        # Put tags button in a row
        for tag, col in zip(row_tags, st.columns(N_TAGS_PER_ROW)):
            if col.button(tag, use_container_width=True):
                st.session_state.filter_selection = tag

# Show posts
for post in filter_posts(posts, st.session_state.filter_selection):
    st.subheader(post.title)
    st.write(f"Summary: {post.summary}")

    left_col, right_col = st.columns(2, gap="medium")

    left_col.subheader("Original tags")
    left_col.write(", ".join(post.tags_original))

    right_col.subheader("GPT-4 tags")
    right_col.write(", ".join(post.tags_gpt))

    with st.expander("🔎 Show more details"):
        st.write("Raw post object in json:")
        st.json(post.model_dump_json())
