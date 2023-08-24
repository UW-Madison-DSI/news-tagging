# News Tagging

Experimental prototype for news tagging using ChatGPT

## Demo

[see demo](https://connect.doit.wisc.edu/dsi-news-tagging/)

## Problem Statement

Given a news article, we want to tag it with relevant labels. For example, given the following news article obtained in this [feed](https://news.wisc.edu/feed/)

## Steps

1. Retrieve news articles by parsing the RSS feed.
2. Use ChatGPT to generate tags for each article.
3. Compile a unique set of tags from those generated.
4. Reorganize and condense the tags using ChatGPT, creating a permanent set of 'main' tags. Store them in `tags.json`.
5. Re-tag the articles using ChatGPT, selecting from the 'main' tags. Include a prompt that allows for the creation of new tags if none of the 'main' tags are applicable (e.g., From this list of 'main' tags, tag this article with one or more tags. If no relevant tags are found, create a new tag).
6. Manually review and potentially iterate on any new tags created.
