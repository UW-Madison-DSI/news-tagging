import requests
from bs4 import BeautifulSoup

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


def html_to_plain_text(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return text


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_taxonomy(post: dict, key: str) -> list[str]:
    taxonomy = {x["taxonomy"]: x["href"] for x in post["_links"]["wp:term"]}
    response = requests.get(taxonomy[key])
    response.raise_for_status()
    output = [x["name"] for x in response.json()]
    if not output:
        return None
    return output


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_taxonomy_from_id(id: str, taxonomy: str) -> list[str]:
    """For repairing empty `post_tag` field."""

    route_map = {
        "category": "categories",
        "post_tag": "tags",
        "syndication": "syndication",
    }

    url = f"https://news.wisc.edu/wp-json/wp/v2/{route_map[taxonomy]}?post={id}"
    response = requests.get(url)
    response.raise_for_status()
    output = [x["name"] for x in response.json()]
    if not output:
        return None
    return output


def parse_wp_post(post: dict) -> dict:
    """Parse a WordPress post into a dictionary."""
    return {
        "id": post["id"],
        "link": post["link"],
        "date_gmt": post["date_gmt"],
        "title": html_to_plain_text(post["title"]["rendered"]),
        "summary": html_to_plain_text(post["excerpt"]["rendered"]),
        "content": html_to_plain_text(post["content"]["rendered"]),
        "category": get_taxonomy(post, "category"),
        "post_tag": get_taxonomy(post, "post_tag"),
        "syndication": get_taxonomy(post, "syndication"),
    }


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def pull_posts(page: int, batch_size: int = 10, order: str = "desc") -> list[dict]:
    response = requests.get(
        f"https://news.wisc.edu/wp-json/wp/v2/posts?per_page={batch_size}&page={page}&order={order}"
    )
    response.raise_for_status()
    return [parse_wp_post(post) for post in response.json()]
