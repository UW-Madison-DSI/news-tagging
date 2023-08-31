import json
import re
from datetime import date
from pathlib import Path

import feedparser
from feedparser.util import FeedParserDict
from pydantic import BaseModel

POSTS_DIR = Path("data/posts")
POSTS_DIR.mkdir(exist_ok=True)
NEWS_URL = "https://news.wisc.edu/feed"


class Post(BaseModel):
    id: str
    author: str
    date: date
    link: str
    title: str
    summary: str
    content: str
    tags_original: list
    tags_gpt: list | None = None
    tags_user: list | None = None

    def save(self, path: Path | None = None) -> None:
        if path is None:
            path = POSTS_DIR / f"{self.id}.json"

        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))

    @classmethod
    def load(self, path: Path) -> "Post":
        with open(path, "r") as f:
            return Post(**json.load(f))


def strip_html_tags(x: str) -> str:
    clean_text = re.sub("<.*?>", "", x)
    return clean_text


def parse_rss_entry(entry: FeedParserDict) -> Post:
    """Parse a single entry from the RSS feed into a News object."""

    d = entry.published_parsed

    return Post(
        id=re.findall(r"\d+", entry.id)[0],
        author=entry.author,
        date=date(d.tm_year, d.tm_mon, d.tm_mday),
        link=entry.link,
        title=entry.title,
        summary=entry.summary,
        content="\n".join([strip_html_tags(con["value"]) for con in entry.content]),
        tags_original=[tag["term"] for tag in entry.tags],
    )


def download_posts(url: str | None = None, save: bool = False) -> list[Post]:
    """Download and save the news data."""

    if url is None:
        url = NEWS_URL

    feed = feedparser.parse(NEWS_URL)
    posts = list(map(parse_rss_entry, feed.entries))

    if save:
        [news.save() for news in posts]

    return posts


def load_posts() -> list[Post]:
    """Load all posts data from the data directory."""

    return [Post.load(path) for path in POSTS_DIR.glob("*.json")]


def get_all_tags(posts: list[Post]) -> list[str]:
    """Get all tags from all posts."""

    tags = []
    for post in posts:
        tags.extend(post.tags_gpt)

    return sorted(list(set(tags)))


def filter_posts(posts: list[Post], tag: str | None) -> list[Post]:
    """Filter posts by tag."""
    if tag is None:
        return posts
    return [post for post in posts if tag in post.tags_gpt]
