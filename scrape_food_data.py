import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# File paths
input_excel_path = '/Users/sandip/Automation/recipes_names.xlsx'
output_excel_path = '/Users/sandip/Automation/scraped_data_output.xlsx'

# Load search data from Excel
search_data = pd.read_excel(input_excel_path)

# List to store scraped data
data_list = []

# Iterate through each recipe name in the Excel file
for recipe_name in search_data['recipe_name']:  # Replace with the actual column name
    try:
        # Open the search page by searching for the keyword
        search_url = f"https://www.bonhappetee.com/food-search/search-page?q={recipe_name}"
        
        # Make the request to the search page
        response = requests.get(search_url)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all results on the page (not just the first result)
        results = soup.find_all('a', class_='sr-result-bar')
        
        if not results:
            print(f"No results found for {recipe_name}")
            continue

        # Loop through all search results
        for result in results:
            # Extract the link to the result page
            result_page_url = "https://www.bonhappetee.com" + result.get('href')

            # Now request the details page for the result
            result_page_response = requests.get(result_page_url)
            result_soup = BeautifulSoup(result_page_response.text, 'html.parser')

            # Scrape the required data from the result page
            try:
                food_name = result_soup.find(class_="food-name").text.strip()
                description = result_soup.find(class_="description").text.strip()
                cuisine_text = result_soup.find(class_="cuisine-text").text.strip()
                serving_size = result_soup.find(class_="serving-size-weight-text").text.strip()

                # Append the scraped data to the list
                data_list.append({
                    "Search Term": recipe_name,
                    "Food Name": food_name,
                    "Description": description,
                    "Cuisine": cuisine_text,
                    "Serving Size": serving_size
                })
            except AttributeError as e:
                print(f"Error scraping data for {recipe_name} from result: {e}")

    except Exception as e:
        print(f"Error processing {recipe_name}: {e}")

# Save the scraped data to an Excel file
df = pd.DataFrame(data_list)
df.to_excel(output_excel_path, index=False)

print(f"Scraping complete. Data saved to {output_excel_path}")