from lxml import html
import requests

import sqlite3

connection = sqlite3.connect('Newspaper_Records.db')
cursor = connection.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS stabroek_days (day TEXT)')

archive_url = 'https://www.stabroeknews.com/archive/'


# Returns the urls of every day in the archive
def get_day_urls(memoize=True):
    page_archive = requests.get(archive_url)
    tree = html.fromstring(page_archive.content)

    day_urls = []

    # Select the dropdown element
    archive_dropdown_options = tree.xpath('//select[@name=\'\\"archive-dropdown\\"\']/option')

    # Loop through the elements of the dropdown to build a list of article pages
    for date_option in archive_dropdown_options:
        day_url = date_option.get('value')

        # Filter out the placeholder option
        if day_url == '\\"\\"':
            continue

        # Filter out days that have already been processed
        if memoize and len(cursor.execute('SELECT 1 FROM articles WHERE Link_to_story = ?', (day_url,)).fetchall()):
            continue

        day_urls.append(day_url)

    return day_urls


# Returns the urls of every article in a day
def get_article_urls(url, memoize=True):
    page_articles = requests.get(url)
    tree = html.fromstring(page_articles.content)

    # Select all article elements
    day_articles = tree.xpath('//article/div/h1/a')
    article_urls = []

    # Loop through each article element and grab the url
    for article in day_articles:

        article_url = article.get('href')

        if not (memoize and len(cursor.execute('SELECT 1 FROM articles WHERE Link_to_story = ?', (article_url,)).fetchall())):
            article_urls.append(article_url)

    return article_urls
