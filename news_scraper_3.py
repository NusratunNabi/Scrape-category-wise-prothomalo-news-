import time
import datetime
from requests_html import HTMLSession
from mysql.connector import Error
from db_connection import create_db_connection
from news_insert import (execute_query,
                                insert_reporter, 
                                insert_category, 
                                insert_news,
                                insert_publisher,
                                insert_image)


def process_and_insert_news_data(connection, publisher_website, publisher, title, reporter, news_datetime, category, news_body, images, url):
        print(f"Error while processing news data - {e}")


def single_news_scraper(url):
    session = HTMLSession()
    try:
        response = session.get(url)
        response.html.render()  # This will download Chromium if not found

        publisher_website = url.split('/')[2]
        publisher = publisher_website.split('.')[-2]

        title = response.html.find('h1', first=True).text
        reporter = response.html.find('.contributor-name', first=True).text
        datetime_element = response.html.find('time', first=True)
        news_datetime = datetime_element.attrs['datetime']
        category = response.html.find('.print-entity-section-wrapper', first=True).text

        news_body = '\n'.join([p.text for p in response.html.find('p')])

        img_tags = response.html.find('img')
        images = [img.attrs['src'] for img in img_tags if 'src' in img.attrs]

        return publisher_website, publisher, title, reporter, news_datetime, category, news_body, images
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    conn = create_db_connection()
    if conn is not None:
        main_link = "https://www.prothomalo.com/bangladesh/capital"
        # collect all news link and process the link
        session = HTMLSession()
        main_response = session.get(main_link)
        all_news_links = main_response.html.find('a')
        for news_link in all_news_links:
            # Extract the href attribute from the anchor tag
            news_url = news_link.attrs.get('href')
            if news_url:
                # Check if the URL is a relative path
                if not news_url.startswith('http'):
                    # Construct the complete URL
                    news_url = f"https://www.prothomalo.com{news_url}"
                # Call the scraper function with the complete URL
                result = single_news_scraper(news_url)
                if result:
                    publisher_website, publisher, title, reporter, news_datetime, category, news_body, images = result
                    print(publisher, title, reporter, news_datetime, category, images)
                    process_and_insert_news_data(conn, publisher_website, publisher, title, reporter, news_datetime, category, news_body, images, news_url)
                else:
                    print(f"Failed to scrape the news link: {news_url}")
            else:
                print("Empty news link found.")
