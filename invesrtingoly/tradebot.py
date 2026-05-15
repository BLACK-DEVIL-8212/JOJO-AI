from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pyautogui
import time
import pytesseract

# Manually specify paths
CHROME_BINARY_PATH = "chrome-win64\\chrome.exe"  # Update if needed
CHROMEDRIVER_PATH = "chromedriver-win64\\chromedriver.exe"  # Update if needed
TESSERACT_PATH = "tesseract-OCR\\tesseract.exe"  # Update if needed

# Configure Chrome options
options = webdriver.ChromeOptions()
options.binary_location = CHROME_BINARY_PATH
options.add_argument("--start-maximized")  # Open browser in maximized mode

# Setup WebDriver with manual ChromeDriver path
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Set Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Open Olymp Trade (assuming you are already logged in)
driver.get("https://olymptrade.com/")
time.sleep(5)  # Wait for page to load

# Function to detect buy/sell signals properly
def check_trade_signal():
    try:
        # Modify these XPaths based on the Olymp Trade UI
        buy_signal = driver.find_elements(By.XPATH, "//*[@class='buy-signal-class']")
        sell_signal = driver.find_elements(By.XPATH, "//*[@class='sell-signal-class']")

        if buy_signal:
            print("💹 Buy Signal Detected!")
            pyautogui.click(1000, 700)  # Temporarily disable clicking
        
        elif sell_signal:
            print("📉 Sell Signal Detected!")
            pyautogui.click(800, 700)  # Temporarily disable clicking
            
        else:
            print("No signal detected.")

    except Exception as e:
        print("Error detecting signals:", e)

# Run the script in a loop
while True:
    check_trade_signal()
    time.sleep(5)  # Check signals every 5 seconds
