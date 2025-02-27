from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv

# Set up Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def get_descriptions_with_timer(url, scrape_duration_seconds, csv_filename):
    # Open the URL in the browser
    driver.get(url)
    time.sleep(2)

    # Get the current time and the time when the scraping should stop
    start_time = datetime.now()
    #user will input time along with url
    end_time = start_time + timedelta(seconds=scrape_duration_seconds)

    # Keep scrolling and scraping until the timer expires
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Run until the timer expires
    while datetime.now() < end_time:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Get the new height of the page
        new_height = driver.execute_script("return document.body.scrollHeight")

        # If the height didn't change, we are at the end of the page
        if new_height == last_height:
            break
        # Update last height to the new height for the next comparison since scrolling should go on
        last_height = new_height

    # Once the timer expires, stop scrolling and start scraping the content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract titles, descriptions, and author names
    # Find all h2 tags (titles)
    titles = soup.find_all('h2')
    # Find all p tags (descriptions)
    descriptions = soup.find_all('p')

    # Create or open a CSV file and write the titles, descriptions, and authors
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Description', 'Author'])  # Write the header row

        # Define phrases to filter out irrelevant descriptions
        irrelevant_phrases = [
            # these are creating title and description mismatched.
            "लगइन",  # Login
            "समीक्षामा भएकोले प्रकाशित भएको छैन",  # Response under review
            "प्रकाशित भएको छैन",  # Not published
        ]

        # Iterate through each title and find the corresponding description and author
        for i in range(len(titles)):
            title_text = titles[i].text.strip()
            description_text = None
            # Default value for the author's name
            author_text = "Unknown"

            # Find the corresponding description near the title
            title_parent = titles[i].find_parent()
            if title_parent:
                # Find a description that is closely related to the current title within the parent container
                sibling_paragraphs = title_parent.find_all_next('p')
                for p_tag in sibling_paragraphs:
                    description_candidate = p_tag.text.strip()
                    if description_candidate and not any(
                            phrase in description_candidate for phrase in irrelevant_phrases):
                        description_text = description_candidate
                        break
                        # Once we find a matching description, we can break out of the loop

                # Find the author in the div with class 'author' and extract text from <a>
                author_div = title_parent.find_parent().find('div',
                                                             class_='author')  # Look for the div with class 'author'
                if author_div:
                    author_tag = author_div.find('a')  # Find the <a> tag inside the div
                    if author_tag:
                        # Extract text from the <a> tag (author's name)
                        author_text = author_tag.text.strip()

            # Skip irrelevant titles and descriptions
            if not description_text or any(phrase in description_text for phrase in irrelevant_phrases):
                continue

            # Write to the CSV file only if the title, description, and author match
            if title_text and description_text:
                writer.writerow([title_text, description_text, author_text])
                print(f"Title: {title_text}")
                print(f"Description: {description_text}")
                print(f"Author: {author_text}\n")

    # Close the browser after scraping
    driver.quit()


# Input the URL and the duration for scraping
# Replace this with the actual URL you want to scrap
url = input("Enter the URL: ")
scrape_duration_seconds = int(input(
    "Put Time in seconds. If you want to use minutes, then use 60 * minutes."))  # Convert the input time to an integer

# Specify the CSV filename
csv_filename = 'truenews.csv'

# Call the function with the provided parameters
get_descriptions_with_timer(url, scrape_duration_seconds, csv_filename)
