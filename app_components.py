import streamlit as st
from data_loader import Post


# Utilities
def get_all_tags(posts: list[Post]) -> list[str]:
    """Get all tags from all posts."""

    tags = []
    for post in posts:
        tags.extend(post.tags)

    return sorted(list(set(tags)))


def filter_posts(posts: list[Post], tags: list[str]) -> list[Post]:
    """Filter posts by tag."""
    if not tags:
        return posts

    filter_tags = set(tags)
    return [post for post in posts if len(set(post.tags).intersection(filter_tags)) > 0]


def header_to_tags(header: str, post: Post) -> str:
    mapping = {
        "Original tags": post.tags_original,
        "GPT-4 tags": post.tags_gpt,
        "User tags": post.tags_user,
    }
    return ", ".join(mapping[header])


def format_user_input(user_input: str) -> list[str]:
    """Format user input into a list of tags."""
    if user_input:
        return [tag.strip().title() for tag in user_input.split(",")]
    else:
        return []


# Components
def tag_filter_component(tags) -> None:
    """Tag filter component."""

    st.subheader("🏷️ Filter articles by Tags")
    st.session_state.filter_selection = st.multiselect("Select tags to filter", tags)


def posts_component(posts: list[Post], with_user_tag: bool) -> None:
    """Posts component."""

    n_columns = 3 if with_user_tag else 2
    tags_headers = ["Original tags", "GPT-4 tags", "User tags"][:n_columns]

    display_posts = filter_posts(posts, st.session_state.filter_selection)
    for post in display_posts:
        st.subheader(post.title)
        st.write(f"Summary: {post.summary}")

        columns = st.columns(n_columns, gap="medium")

        for i, col in enumerate(columns):
            header = tags_headers[i]
            col.subheader(header)
            col.write(header_to_tags(header, post))

        with st.expander("🔎 Show technical details"):
            st.json(post.model_dump_json())
