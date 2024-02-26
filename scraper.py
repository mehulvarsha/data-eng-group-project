
"""
YouTube Video Data Scraper

This script fetches video data from the YouTube Data API for various countries, including video statistics and metadata,
and saves the results as CSV files. It aims to collect comprehensive information about trending videos in different regions.

"""

# requests: for making HTTP requests.
# sys: for interacting with the Python interpreter.
# time: for handling time-related operations.
# os: for interacting with the operating system.
# argparse: for parsing command-line arguments.
# json: for working with JSON data.
# Importing Libraries
import requests, sys, time, os, argparse, json

# Constant and Variable Initialization
# video_file_features: A list of features that will be extracted from each video snippet.
video_file_features = ["title",
                    "publishedAt",
                    "channelId",
                    "channelTitle",
                    "categoryId"]

# unsafe_characters: Characters that need to be excluded from the output, typically problematic in CSV files.
not_included_characters = ['\n', '"']

# column_header: Column headers for the CSV file, including video information and statistics.
column_header = ["video_id"] + video_file_features + ["trending_date", "tags", "view_count", "likes", "dislikes",
                                            "comment_count", "thumbnail_link", "comments_disabled",
                                            "ratings_disabled", "description"]


# api_country_code_read(api_path, code_path): Reads API key and country codes from files.
def api_country_code_read(api_path, code_path):
    # Open the file containing the API key
    with open(api_path, 'r') as file:
        # Read the API key from the file
        api_key = file.readline()

    # Open the file containing the country codes
    with open(code_path) as file:
        # Read all lines from the file and remove trailing newline characters
        country_codes = [x.rstrip() for x in file]

    # Return the API key and country codes
    return api_key, country_codes

# handle_not_included_char(feature): Prepares a feature for CSV output by removing unsafe characters and enclosing it in quotes.
def handle_not_included_char(feature):
    # Iterate over each unsafe character
    for ch in not_included_characters:
        # Replace each occurrence of the unsafe character with an empty string
        feature = str(feature).replace(ch, "")
    # Surround the feature with double quotes and return it
    return f'"{feature}"'


# fetch_video_data(page_token, country_code): Makes an API request to YouTube using a page token and a country code.
def fetch_video_data(page_token, country_code):
    # Construct the URL for the YouTube Data API request
    request_url = f'https://www.googleapis.com/youtube/v3/videos?part=id,statistics,snippet{page_token}chart=mostPopular&regionCode={country_code}&maxResults=50&key=AIzaSyBefTakB382MdVQrs0s_n2izpFT4WyaCTk'   
    # Make a GET request to the YouTube Data API
    response = requests.get(request_url)
    # Check if the request was rate-limited (HTTP status code 429)
    if response.status_code == 429:
        # Print a message indicating temporary ban due to excess requests
        print("Temp-Banned due to excess requests, please wait and continue later")
        # Exit the script
        sys.exit()
    # Parse the JSON response and return it
    return response.json()

# prepare_tags(tags_list): Formats tags into a string separated by pipe characters.
def prepare_tags(tags_list):
    # Join the tags in the list into a single string separated by the pipe character
    tags_string = "|".join(tags_list)
    # Prepare the tags string by removing unsafe characters and enclosing it in quotes
    prepared_tags = handle_not_included_char(tags_string)
    # Return the prepared tags
    return prepared_tags

# Extracts video data from API response.
def extract_video_data(items):
    # Initialize an empty list to store formatted video data
    lines = []
    # Iterate through each video item
    for video in items:
        comments_disabled = False  # Initialize variables to track comments and ratings status
        ratings_disabled = False

        # Check if the video has statistics information
        if "statistics" not in video:
            # If statistics are missing, skip this video
            continue

        # Extract video ID and prepare it for output
        video_id = handle_not_included_char(video['id'])

        # Extract snippet and statistics sub-dicts from the video
        snippet = video['snippet']
        statistics = video['statistics']

        # Extract features from the snippet that require no special processing
        features = [handle_not_included_char(snippet.get(feature, "")) for feature in video_file_features]

        # Extract special case features or features not within the snippet dict
        description = snippet.get("description", "")
        thumbnail_link = snippet.get("thumbnails", dict()).get("default", dict()).get("url", "")
        trending_date = time.strftime("%y.%d.%m")
        tags = prepare_tags(snippet.get("tags", ["[none]"]))
        view_count = statistics.get("viewCount", 0)

        # Check if likes and dislikes are available in the statistics dict
        if 'likeCount' in statistics and 'dislikeCount' in statistics:
            likes = statistics['likeCount']
            dislikes = statistics['dislikeCount']
        else:
            # If likes or dislikes are missing, mark ratings as disabled
            ratings_disabled = True
            likes = 0
            dislikes = 0
        
        # Check if comment count is available in the statistics dict
        if 'commentCount' in statistics:
            comment_count = statistics['commentCount']
        else:
            # If comment count is missing, mark comments as disabled
            comments_disabled = True
            comment_count = 0

        # Compile all data into a single formatted line        
        line = [video_id] + features + [handle_not_included_char(x) for x in [trending_date, tags, view_count, likes, dislikes,
                                                                       comment_count, thumbnail_link, comments_disabled,
                                                                       ratings_disabled, description]]
        # Join the line elements with commas and append to the list of lines
        lines.append(",".join(line))

     # Return the list of formatted lines
    return lines


# fetch_all_pages(country_code, next_page_token="&"): Retrieves data from multiple pages of API response.
def fetch_all_pages(country_code, next_page_token="&"):
    country_data = []  # Initialize an empty list to store video data for the country

    # Iterate through each page of video data until there are no more pages
    while next_page_token is not None:
        # A page of data i.e. a list of videos and all needed data
        # Request data for a page of videos using the YouTube Data API
        video_data_page = fetch_video_data(next_page_token, country_code)

        # Get the next page token and build a string which can be injected into the request with it, unless it's None,
        # then let the whole thing be None so that the loop ends after this cycle
       
        # Get the next page token from the response, if available
        next_page_token = video_data_page.get("nextPageToken", None)
        # Construct the page token string for the next request, or set it to None if there are no more pages
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

        # Extract video information from the current page and append to the country data list
        items = video_data_page.get('items', [])
        country_data += extract_video_data(items)

    # Return the collected video data for the country
    return country_data

# write_to_files(country_code, country_data): Writes data to CSV file for a specific country code.
def write_to_files(country_code, country_data):
    # Print a message indicating that data for the country is being written to files
    print(f"Writing {country_code} data to files...")

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write CSV file
    with open(f"{output_dir}/{time.strftime('%y.%d.%m')}_{country_code}_videos.csv", "w+", encoding='utf-8') as csv_file:
        # Iterate through each row of video data and write it to the CSV file
        for row in country_data:
            csv_file.write(f"{row}\n")


# fetch_and_write_data(): Automates the retrieval of video data from the YouTube Data API for multiple countries and stores this data in files for analysis.
def fetch_and_write_data():
    # Iterate through each country code to fetch and write data
    for country_code in country_codes:
        # Retrieve video data for the current country
        country_data = [",".join(column_header)] + fetch_all_pages(country_code)
        # Write the retrieved data to files
        write_to_files(country_code, country_data)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--key_path', help='Path to the file containing the api key, by default will use api_key.txt in the same directory', default='api_key.txt')
    parser.add_argument('--country_code_path', help='Path to the file containing the list of country codes to scrape, by default will use country_codes.txt in the same directory', default='country_codes.txt')
    parser.add_argument('--output_dir', help='Path to save the outputted files in', default='output/')

    # Set the output directory
    args = parser.parse_args()
    output_dir = args.output_dir
    
    # Read API key and country codes from files
    api_key, country_codes = api_country_code_read(args.key_path, args.country_code_path)

    # Fetch and write video data for each country
    fetch_and_write_data()
