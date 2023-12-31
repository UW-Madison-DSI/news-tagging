import peewee
import asyncio
import ast
import streamlit as st
from cachetools import TTLCache, cached
from app_components import (
    Post,
    tag_filter_component,
    posts_component,
    splash_screen_component,
    format_user_input,
    get_all_tags,
)
from database import Post as DBPost
from gpt import tag, batch_user_tag

st.set_page_config(page_title="UW News tagging", page_icon="📰", layout="wide")

# Initialize session state
if "filter_selection" not in st.session_state:
    st.session_state.filter_selection = []

for var in ["user_tags", "user_input", "posts"]:
    if var not in st.session_state:
        st.session_state[var] = None


@cached(cache=TTLCache(maxsize=1, ttl=600))
def get_posts(n: int = 10) -> list[Post]:
    """Get 10 random post from local DB."""

    pub_date = peewee.fn.DATETIME(DBPost.date_gmt).alias("pub_date")
    query = (
        DBPost.select(
            DBPost.id,
            DBPost.title,
            DBPost.summary,
            DBPost.content,
            DBPost.category,
            DBPost.post_tag,
            DBPost.syndication,
            pub_date,
        )
        .order_by(pub_date.desc())
        .limit(n)
    )

    posts = []
    for x in query.dicts():
        posts.append(
            Post(
                id=x["id"],
                pub_date=x["pub_date"],
                title=x["title"],
                summary=x["summary"],
                content=x["content"],
                category=ast.literal_eval(x["category"]) if x["category"] else [],
                post_tag=ast.literal_eval(x["post_tag"]) if x["post_tag"] else [],
                syndication=ast.literal_eval(x["syndication"])
                if x["syndication"]
                else [],
                tags_gpt=tag(f"{x['title']} {x['summary']}"),
            )
        )

    return posts


async def async_get_user_tags(posts: list[Post], user_tags: list[str]) -> list[Post]:
    texts = [f"{post.title} {post.summary}" for post in posts]
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
