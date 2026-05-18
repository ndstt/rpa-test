from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

import re
from pathlib import Path
from urllib.parse import urljoin

from data import *
from config import *

# login
def login(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    try:
        print("|----------------LOGIN----------------|")
        driver.get(LOGIN_URL)

        print("Waiting for cookie button...")
        # wait for cookie button appear and accept it
        cookie_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.cwc-accept-button"
            ))
        )
        print("Clicking cookie button...")
        cookie_button.click()

        print("Waiting for login form...")
        # Get element of username, password and login button
        username_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        print("Filling login form and submitting...")
        # Fill in the login form and submit
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        login_button.click()
    
        print("Waiting for main page...")
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
        print("Navigating to course page (1)")
        driver.get(COURSE_PAGE_URL)

        print("finding course categories...")
        non_category_values = {
            "COURSE",
            "WORKSHOP",
            "beginner",
            "intermediate",
            "advanced",
            "free",
            "BUNDLE",
        }

        def get_category_values() -> list[str]:
            values = driver.execute_script(
                """
                return [...document.querySelectorAll("input[type='checkbox']")]
                    .map(input => input.value)
                    .filter(Boolean);
                """
            )
            return [
                value
                for value in values
                if value not in non_category_values
            ]

        print("Extracting course category URLs...")
        categories = wait.until(
            lambda _: get_category_values()
            if "ai" in get_category_values()
            else False
        )

        print(categories)

        print("Already get all course category URLs")
        return categories

    except Exception as e:
        print("Failed to get course categories:")
        print(e)

    print("|------------------------------------------------------|")
    return []

# get courses url and its category in each category. each course can be in multiple category
def get_courses_url_in_category(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    course_category: str,
    max_retries: int = 3,
) -> tuple[list[CourseCategory], set[str]]:
    for attempt in range(1, max_retries + 1):
        try:
            return _get_courses_url_in_category(driver, course_category)
        except Exception as e:
            print(f"Failed to get course in {course_category} (attempt {attempt}/{max_retries}):")
            print(e)
            if attempt < max_retries:
                print("Retrying...")

    print(f"Skip category after {max_retries} failed attempts: {course_category}")
    print("|-----------------------------------------------------------------------|")
    return [], set()


def _get_courses_url_in_category(
    driver: webdriver.Chrome,
    course_category: str,
) -> tuple[list[CourseCategory], set[str]]:
        print(f"|---------------GETTING COURSE IN {course_category.upper()}---------------|")
        driver.get(COURSE_CATEGORY_PREFIX + course_category)
        category_wait = WebDriverWait(driver, 20)

        course_link_selector = "a[href^='/courses/']"
        load_more_text = "\u0e14\u0e39\u0e04\u0e2d\u0e23\u0e4c\u0e2a\u0e40\u0e1e\u0e34\u0e48\u0e21"

        def get_course_urls() -> list:
            return driver.execute_script(
                """
                return [...new Set(
                    [...document.querySelectorAll(arguments[0])]
                        .map(a => a.href)
                        .filter(Boolean)
                )];
                """,
                course_link_selector
            )

        def find_load_more_button():
            return driver.execute_script(
                """
                return [...document.querySelectorAll('button')]
                    .find(btn =>
                        btn.textContent.includes(arguments[0]) &&
                        !btn.disabled &&
                        (btn.offsetWidth || btn.offsetHeight || btn.getClientRects().length)
                    ) || null;
                """,
                load_more_text
            )

        category_wait.until(lambda _: len(get_course_urls()) > 0)

        while True:
            before_count = len(get_course_urls())
            print(f"Try clicking 'Load More' button... ({before_count} courses loaded)")

            try:
                load_more_button = category_wait.until(lambda d: find_load_more_button())
            except TimeoutException:
                print("No more 'Load More' button found.")
                break

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                load_more_button
            )
            driver.execute_script("arguments[0].click();", load_more_button)

            try:
                category_wait.until(lambda d: len(get_course_urls()) > before_count)
            except TimeoutException:
                after_count = len(get_course_urls())
                if after_count == before_count:
                    print("Clicked 'Load More', but no new courses appeared. Stop to avoid infinite loop.")
                    break

        course_urls = get_course_urls()
        course_url_set = set(course_urls)
        course_and_category = [
            CourseCategory(
                url=url,
                category=course_category
            )
            for url in course_urls
        ]

        print(f"Already get all course URLs ({len(course_url_set)} courses)")
        return course_and_category, course_url_set

# get courses url and its category in every category
def get_courses_url(driver: webdriver.Chrome, wait: WebDriverWait) -> tuple:
    categories = get_course_categories(driver, wait)
    course_and_category_list = []
    course_url_list = set()

    for category_url in categories:
        courses_in_category, course_urls = get_courses_url_in_category(driver, wait, category_url)
        course_and_category_list.extend(courses_in_category)
        course_url_list.update(course_urls)

    return course_and_category_list, course_url_list

def get_first_number(text: str, default: int = 0) -> int:
    match = re.search(r"\d+", text)
    if match is None:
        return default
    return int(match.group())


def get_first_float(text: str, default: float = 0.0) -> float:
    clean_text = text.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", clean_text)
    if match is None:
        return default
    return float(match.group())


def get_review_highlight_percentages(review_card) -> dict[str, int]:
    lines = [
        line.strip()
        for line in review_card.text.splitlines()
        if line.strip()
    ]

    try:
        section_start = lines.index("สิ่งที่ผู้เรียนชอบมากที่สุด") + 1
    except ValueError:
        return {}

    section_end = next(
        (
            index
            for index in range(section_start, len(lines))
            if lines[index].startswith("ความคิดเห็น")
        ),
        len(lines)
    )

    percentages = {}
    section_lines = lines[section_start:section_end]
    for index, line in enumerate(section_lines):
        same_line_match = re.fullmatch(r"(.+?)\s+(\d+)\s*%", line)
        if same_line_match:
            percentages[same_line_match.group(1).strip()] = int(same_line_match.group(2))
            continue

        if index + 1 >= len(section_lines):
            continue

        next_line_match = re.fullmatch(r"(\d+)\s*%", section_lines[index + 1])
        if next_line_match:
            percentages[line] = int(next_line_match.group(1))

    return percentages


def get_instructor_name(instructor_card) -> str:
    matched_elements = instructor_card.find_elements(
        By.CSS_SELECTOR,
        "div[color='COURSE_DETAILS'][font-weight='medium']"
    )
    if matched_elements:
        return matched_elements[0].text.strip()

    lines = [
        line.strip()
        for line in instructor_card.text.splitlines()
        if line.strip() and line.strip() != "ผู้สอน"
    ]
    if not lines:
        return ""
    return lines[0]


def get_course_detail(driver: webdriver.Chrome, wait: WebDriverWait, course_url: str) -> CourseDetail:
    try:
        print(f"|---------------GETTING {course_url} DETAIL---------------|")
        course_url = urljoin(URL, course_url)
        driver.get(course_url)

        # wait for the course title to be present and get it
        course_hero_card = wait.until(
            EC.presence_of_element_located((By.ID, "hero-detail"))
        )
        print("Course hero card found, extracting course detail...")

        # course hero
        course_title = course_hero_card.find_element(
            By.CSS_SELECTOR,
            "h1"
        ).text.strip()

        overview_card = driver.find_element(
            By.CSS_SELECTOR,
            "div[id='overview']"
        )
        course_overview = overview_card.find_element(
            By.CSS_SELECTOR,
            "div[color='COURSE_DETAILS'][font-size='2'][font-weight='light'][font-family='content']"
        ).text.strip()

        course_cost = course_hero_card.find_element(
            By.CSS_SELECTOR,
            "#hero-detail div[color='COURSE_DETAILS']"
        ).text.strip()
        course_cost = get_first_float(course_cost)

        instructor_card = driver.find_element(By.ID, "instructor")
        instructor_name = get_instructor_name(instructor_card)

        # review detail
        avg_rating = course_hero_card.find_element(
            By.CSS_SELECTOR,
            "span[color='primary'][font-size='2'][font-weight='medium']"
        ).text.strip()
        avg_rating = get_first_float(avg_rating)

        review_card = driver.find_element(By.ID, "course-reviews")
        total_reviews = review_card.find_element(
            By.CSS_SELECTOR,
            "span[color='textV3.darkAlt'][font-family='FONT_V3.main'][font-size='2'][font-weight='medium']"
        ).text.strip()
        total_reviews = get_first_number(total_reviews)

        overall_satisfaction_percentage = review_card.find_element(
            By.XPATH,
            ".//*[contains(text(), 'ของรีวิว')]/preceding::p[contains(text(), '%')][1]"
        ).text.strip()
        overall_satisfaction_percentage = get_first_number(overall_satisfaction_percentage)

        review_highlight_percentages = get_review_highlight_percentages(review_card)

        course_detail = CourseDetail(
            url=course_url,
            title=course_title,
            cost=course_cost,
            overview=course_overview,
            instructor_name=instructor_name,
            avg_rating=avg_rating,
            total_reviews=total_reviews,
            overall_satisfaction_percentage=overall_satisfaction_percentage,
            review_highlight_percentages=review_highlight_percentages,
        )

        print("|--------------------------------------------------|")
        return course_detail

    except Exception as e:
        print("Failed to get course detail:")
        print(e)
        raise


def get_all_course_details(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    course_url_list: set[str],
) -> list[CourseDetail]:
    course_details: list[CourseDetail] = []

    print(f"|---------------GETTING ALL COURSE DETAILS ({len(course_url_list)} courses)---------------|")
    for index, course_url in enumerate(sorted(course_url_list), start=1):
        print(f"Getting course detail {index}/{len(course_url_list)}")
        try:
            course_detail = get_course_detail(driver, wait, course_url)
            course_details.append(course_detail)
        except Exception as e:
            print(f"Skip course because getting detail failed: {course_url}")
            print(e)

    print(f"Already get all course details ({len(course_details)} courses)")
    print("|-----------------------------------------------------------------------|")
    return course_details


def export_to_excel(
    course_and_category: list[CourseCategory],
    course_details: list[CourseDetail],
    file_path: str = "data/skooldio_courses.xlsx",
) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    course_category_df = pd.DataFrame(course_and_category)
    course_detail_df = pd.DataFrame(course_details)
    course_review_highlights = [
        CourseReviewHighlight(
            url=course_detail["url"],
            label=label,
            percentage=percentage,
        )
        for course_detail in course_details
        for label, percentage in course_detail["review_highlight_percentages"].items()
    ]
    course_review_highlight_df = pd.DataFrame(course_review_highlights)

    if "review_highlight_percentages" in course_detail_df.columns:
        course_detail_df = course_detail_df.drop(columns=["review_highlight_percentages"])

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        course_detail_df.to_excel(writer, sheet_name="course_details", index=False)
        course_category_df.to_excel(writer, sheet_name="course_categories", index=False)
        course_review_highlight_df.to_excel(writer, sheet_name="review_highlights", index=False)

    print(f"Exported Excel file: {file_path}")


if __name__ == "__main__":
    options = Options()
    options.add_argument("--start-maximized")

    scraped_data: list[CourseDetail] = []
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    login(driver, wait)
    course_and_category, course_url_list = get_courses_url(driver, wait)
    course_details = get_all_course_details(driver, wait, course_url_list)
    export_to_excel(course_and_category, course_details)
