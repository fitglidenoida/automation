import time
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

# Set up Chrome options for debugging
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start with full window
chrome_options.add_argument("--disable-infobars")  # Remove automation banners
chrome_options.add_argument("--disable-extensions")
chrome_options.headless = False  # Disable headless for debugging

# Explicit ChromeDriver setup
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to scrape recipe details
def scrape_recipe(url):
    driver.get(url)
    time.sleep(2)  # Wait for the page to load completely
    try:
        recipe_title = driver.find_element(By.CSS_SELECTOR, "h1").text
        ingredients = driver.find_elements(By.CSS_SELECTOR, ".mntl-structured-ingredients__list-item")
        ingredients_list = [ingredient.text for ingredient in ingredients]
        print(f"Scraped recipe: {recipe_title}")
        return recipe_title, ingredients_list
    except Exception as e:
        print(f"Error scraping recipe {url}: {e}")
        return None, None

# Function to save data to Excel
def save_to_excel(filename, recipe_title, ingredients):
    try:
        # Open or create the workbook
        try:
            workbook = openpyxl.load_workbook(filename)
            sheet = workbook.active
        except FileNotFoundError:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["Recipe Title", "Ingredients"])  # Add headers

        # Append data to the sheet
        sheet.append([recipe_title, ", ".join(ingredients)])
        workbook.save(filename)
        print(f"Saved: {recipe_title}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

# Function to scrape all recipes in a category
def scrape_category(category_url, filename):
    driver.get(category_url)
    print(f"Navigating to: {category_url}")
    time.sleep(3)  # Wait for the page to load

    try:
        # Locate all sections dynamically
        recipe_sections = driver.find_elements(By.CSS_SELECTOR, "[id^='mntl-taxonomysc-article-list-group']")

        for section in recipe_sections:
            cards = section.find_elements(By.CSS_SELECTOR, ".mntl-card-list-items")

            for card in cards:
                try:
                    ActionChains(driver).move_to_element(card).click().perform()
                    time.sleep(2)

                    # Scrape the recipe details
                    recipe_title, ingredients = scrape_recipe(driver.current_url)

                    if recipe_title and ingredients:
                        save_to_excel(filename, recipe_title, ingredients)

                    # Return to the previous page
                    driver.back()
                    time.sleep(2)
                except Exception as e:
                    print(f"Error scraping card: {e}")
                    continue

    except Exception as e:
        print(f"Error scraping category: {e}")

# Main function
def main():
    category_url = "https://www.allrecipes.com/recipes/15935/world-cuisine/asian/indian/drinks/"
    filename = "scraped_indian_drinks_recipes.xlsx"
    scrape_category(category_url, filename)
    driver.quit()

if __name__ == "__main__":
    main()