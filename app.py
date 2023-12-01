import logging
import asyncio
import streamlit as st
from cachetools import TTLCache, cached
from app_components import (
    tag_filter_component,
    posts_component,
    splash_screen_component,
    format_user_input,
    get_all_tags,
)
from data_loader import Post, download_posts, load_posts
from gpt import tag, batch_user_tag

st.set_page_config(page_title="UW News tagging", page_icon="📰", layout="wide")

# Initialize session state
if "filter_selection" not in st.session_state:
    st.session_state.filter_selection = []

for var in ["user_tags", "user_input", "posts"]:
    if var not in st.session_state:
        st.session_state[var] = None


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
        post.tags_gpt = tag(post.to_text())
        post.save()

    existing_posts.extend(new_posts)
    return existing_posts


async def async_get_user_tags(posts: list[Post], user_tags: list[str]) -> list[Post]:
    texts = [post.to_text() for post in posts]
    news_user_tags = await batch_user_tag(texts, user_tags)
    for post, tags in zip(posts, news_user_tags):
        post.tags_user = tags
    return posts


@st.cache_data
def get_user_tags(_posts: list[Post], user_tags: list[str]) -> list[Post]:
    """Append user tags to posts."""

    return asyncio.run(async_get_user_tags(_posts, user_tags))


def run() -> None:
    """Run the data pipeline."""

    st.session_state.posts = get_posts()
    st.session_state.user_tags = format_user_input(st.session_state.user_input)

    # Process user tags
    if st.session_state.user_tags:
        st.session_state.posts = get_user_tags(
            st.session_state.posts, st.session_state.user_tags
        )


# Sidebar
with st.sidebar:
    st.subheader("💡 User defined tags")
    st.write(
        "You have the option to supply your own set of tags for news categorization. \
            Alternatively, simply hit 'Run' without tags."
    )
    st.session_state.user_input = st.text_input(
        "Optionally enter a list of custom tags (comma separated)",
        key="custom_tags",
        placeholder="e.g. physics, astronomy, space, psychology",
    )

    if st.button("Run"):
        run()

    if st.session_state.posts:
        tags = get_all_tags(st.session_state.posts)
        tag_filter_component(tags)


# Main content
if not st.session_state.posts:
    # Have not run the data pipeline yet
    splash_screen_component()
else:
    # Already ran the data pipeline
    posts_component(
        st.session_state.posts, with_user_tag=bool(st.session_state.user_tags)
    )
