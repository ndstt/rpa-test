from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import *

# login
def login(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    try:
        print("|----------------LOGIN----------------|")
        driver.get(LOGIN_URL)

        # wait for cookie button appear and accept it
        cookie_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.cwc-accept-button"
            ))
        )
        cookie_button.click()

        # Get element of username, password and login button
        username_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Fill in the login form and submit
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        login_button.click()

        # Wait until the URL changes to the main page URL to confirm login success
        wait.until(
            EC.url_to_be(MAIN_PAGE_URL)
        )
        print("Login success")

    except Exception as e:
        print("Login failed")
        print(e)

    print("|-------------------------------------|")
    print()

# get course categories
def get_course_categories(driver: webdriver.Chrome, wait: WebDriverWait) -> list:
    try:
        print("|---------------GETTING COURSE CATEGORIES---------------|")
        driver.get(COURSE_PAGE_URL)

        # clear the screen
        close_popup = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "img.widget.widget-popupcloser"))
        )
        print("popup found, try to close it...")
        close_popup.click()
        print("popup closed")

        # Wait for the course categories to be present and get them
        course_categories_box = wait.until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//p[normalize-space()='เลือกหมวดหมู่']/following-sibling::div[1]"
            ))
        )

        course_categories = course_categories_box.find_elements(By.CSS_SELECTOR, "span[font-size='2', font-weight='medium']")

        category_url_list = []
        for course_category in course_categories:
            print()
            category_url_list.append(COURSE_CATEGORY_PREFIX + course_category.text.strip().lower())

        print("Already get all course category URLs")
        return category_url_list

    except Exception as e:
        print("Failed to get course categories:")
        print(e)

    print("|------------------------------------------------------|")

# get courses url in each category
def get_courses_url_in_category(driver: webdriver.Chrome, wait: WebDriverWait, course_category_url: str) -> list:
    try:
        print("|---------------GETTING COURSE---------------|")
        driver.get(course_category_url)

        while True:
            print("Try clicking 'Load More' button...")
            try:
                # find the "Load More" button
                load_more_button = wait.until(lambda d: d.execute_script("""
                return [...document.querySelectorAll('button')]
                .find(btn => btn.textContent.includes('ดูคอร์สเพิ่ม'));
            """))
                # scroll the "Load More" button into view and click it
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    load_more_button
                )
                load_more_button.click()
            except TimeoutException:
                print("No more 'Load More' button found. All courses should be loaded.")
                break

        # wait for the course boxes to be present and get them
        course_boxes = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href^='/courses/']"))
        )

        course_url_list = [MAIN_PAGE_URL + course_box.get_attribute("href") for course_box in course_boxes]
        print("Already get all course URLs")
        return course_url_list

    except Exception as e:
        print("Failed to get course:")
        print(e)

    print("|--------------------------------------------|")

# get courses url in every category
def get_courses_url(driver: webdriver.Chrome, wait: WebDriverWait) -> list:
    categories = get_course_categories(driver, wait)
    course_url_list = []
    for category_url in categories:
        courses_in_category = get_courses_url_in_category(driver, wait, category_url)
        course_url_list.extend(courses_in_category)
    return course_url_list

def get_course_detail(driver: webdriver.Chrome, wait: WebDriverWait, course_suffix: str) -> None:
    try:
        print(f"|---------------GETTING {course_suffix} DETAIL---------------|")
        course_url = URL + course_suffix
        driver.get(course_url)
        # wait for the course title to be present and get it
        course_hero_card = wait.until(
            EC.presence_of_element_located((By.ID, "hero-card"))
        )

        # course hero
        course_title = course_hero_card.find_element(By.CSS_SELECTOR, "h1").text
        course_type = course_hero_card.find_element(By.CSS_SELECTOR, "div[color='primary', font-size='1', font-weight='medium']").text
        course_summary = course_hero_card.find_element(By.CSS_SELECTOR, "p").text
        course_cost = course_hero_card.find_element(By.CSS_SELECTOR, "#hero-detail div[color='COURSE_DETAILS']").text
        course_rating = course_hero_card.find_element(By.CSS_SELECTOR, "span[color='primary', font-size='1', font-weight='medium']").text

        # course detail
        course_detail_card = driver.find_element(By.ID, "overview")
        course_detail = course_detail_card.find_element(By.CSS_SELECTOR, "div[font-family='content']").text.strip()

        # instructor detail
        instructor_card = driver.find_element(By.ID, "instructor")
        instructor_name = instructor_card.find_element(
            By.CSS_SELECTOR,
            "div[color='COURSE_DETAILS'][font-weight='medium']"
        ).text.strip()
        instructor_position = instructor_card.find_element(
            By.CSS_SELECTOR,
            "div[color='COURSE_DETAILS'][font-weight='exLight']"
        ).text.strip()

        # review detail
        review_card = driver.find_element(By.ID, "course-reviews")
        reviews = []


    except Exception as e:
        print("Failed to get course detail:")
        print(e)

    print("|--------------------------------------------------|")

if __name__ == "__main__":
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    login(driver, wait)
    get_course_categories(driver, wait)
    '''course_urls = get_courses_url(driver, wait)

    for course_url in course_urls:
        print(course_url)'''