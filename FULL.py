import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException  # Importing the exception
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start maximized
chrome_options.add_argument("--disable-notifications")  # Disable notifications

# Initialize WebDriver (no need to specify a driver path with Selenium 4+)
driver = webdriver.Chrome(options=chrome_options)

# Open the site to set cookies
driver.get("https://civitai.com")

# Load cookies from the JSON file
with open("cookies.json", "r") as f:
    cookies = json.load(f)

# Add each cookie to the browser
for cookie in cookies:
    if "sameSite" not in cookie or cookie["sameSite"] not in ["Strict", "Lax", "None"]:
        cookie["sameSite"] = "Lax"  # Default value
    cookie.pop("expiry", None)  # Remove 'expiry' to avoid issues
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print(f"Failed to add cookie: {cookie}. Error: {e}")

# Refresh the page to apply the cookies and load the logged-in session
driver.refresh()

# Navigate to the images page
driver.get("https://civitai.com/images")

# Define the button emojis to click
button_emojis_to_click = ["👍", "❤️", "😂", "😢"]

# Function to click a button using JavaScript
def click_button(button):
    driver.execute_script("arguments[0].click();", button)

# Function to scroll down a little
def scroll_down(pixels=300):
    driver.execute_script(f"window.scrollBy(0, {pixels});")  # Scroll down by specified pixels
    time.sleep(0.1)  # Add a short delay to allow scrolling to settle

# Function to repeatedly click matching buttons every 3 seconds
try:
    while True:
        # Find all buttons with the attribute data-button="true"
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-button='true']")

        # Loop through each button and click it if its text matches our criteria
        for button in buttons:
            try:
                button_text_elements = button.find_elements(By.CLASS_NAME, "mantine-Text-root")
                button_texts = [text_elem.text for text_elem in button_text_elements]

                # Check if any of the button texts match the specified emojis
                if any(text in button_texts for text in button_emojis_to_click):
                    # Wait until the button is clickable
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(button))

                    # Scroll the button into view
                    driver.execute_script("arguments[0].scrollIntoView();", button)

                    click_button(button)  # Use JavaScript click method
                    print(f"Button clicked: {button_texts}")

                    # Scroll down a little after each click
                    scroll_down()

            except StaleElementReferenceException:
                print("StaleElementReferenceException encountered. Skipping to the next button.")

        # Wait 3 seconds before the next iteration
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    driver.quit()  # Close the browser after stopping the script
