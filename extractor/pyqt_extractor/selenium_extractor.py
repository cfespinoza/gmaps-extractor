from bs4 import BeautifulSoup
from selenium import webdriver

# url = "https://www.google.com/maps/search/Restaurants/28047/"
url = "https://www.google.com/maps/search/Restaurants/@40.3995807,-3.771754,15z"
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.": 2})
chromeOptions.add_argument("--no-sandbox")
chromeOptions.add_argument("--disable-setuid-sandbox")

chromeOptions.add_argument("--remote-debugging-port=9222")  # this

chromeOptions.add_argument("--disable-dev-shm-using")
chromeOptions.add_argument("--disable-extensions")
chromeOptions.add_argument("--disable-gpu")
chromeOptions.add_argument("start-maximized")
chromeOptions.add_argument("disable-infobars")
chromeOptions.add_argument("--headless")
# initialize the driver
driver = webdriver.Chrome(
    executable_path="/home/cflores/cflores_workspace/google_maps_exractor/notebooks_test/chromedriver",
    chrome_options=chromeOptions)
driver.implicitly_wait(30)
driver.get(url)
driver.implicitly_wait(10)

attrs_lateral_restaurant_list = {
    'class': 'section-result',
    'role': 'listitem'}
soup_level = BeautifulSoup(driver.page_source, 'lxml')
for restaurant in soup_level.find_all('div', attrs=attrs_lateral_restaurant_list):
    print(restaurant)



driver.quit()