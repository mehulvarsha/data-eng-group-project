"""
YouTube Video Categories Scraper

This script fetches video categories data for various countries from the YouTube Data API and saves the results as JSON files.

The aim of this scraper is to gather information about the available video categories in different countries on YouTube.

"""
import os
import json
import requests

# Read API key from file
api_key_path = "api_key.txt"
with open(api_key_path, "r") as f:
    API_KEY = f.read().strip()[1:-1]  # Remove square brackets

# Read country codes from file
country_codes_path = "country_codes.txt"
with open(country_codes_path, "r") as f:
    country_codes = [line.strip() for line in f]

# Directory to save output files
output_dir = "output"

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Dictionary to store video categories for each country code
video_categories = {}

# Iterate over each country code and fetch video categories
for country_code in country_codes:
    # Construct the request URL
    url = f"https://www.googleapis.com/youtube/v3/videoCategories?key={API_KEY}&part=snippet&regionCode={country_code}"

    # Send GET request to the API
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()

        # Write JSON data to file
        output_file = os.path.join(output_dir, f"{country_code}_video_categories.json")
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
    else:
        # Print error message if request failed
        print(f"Failed to fetch video categories for {country_code}. Status code: {response.status_code}")

# Print confirmation
print("Video categories data saved in the output directory.")
