from os import path
from glob import glob
from playwright.sync_api import sync_playwright


PROFILE_PATH = ""


def add_expected_schedule(date, headless):
    with sync_playwright() as playwright:
        browser, page = get_browser_and_page(playwright, date, headless)
        user_id = get_current_user_id(page)
        year, month, day = (date.year, date.month, date.day)
        add_expected_schedule_at_date_for_user(page, user_id, year, month, day)
        browser.close()


def get_browser_and_page(playwright, date, headless):
    firefox = playwright.firefox
    browser = firefox.launch_persistent_context(
        user_data_dir=PROFILE_PATH or _get_default_firefox_profile(),
        headless=headless,
        args=["--new-tab"],
    )
    page = browser.pages[0]
    return browser, page


def _get_default_firefox_profile():
    profile_path = path.expanduser("~/Library/Application Support/Firefox/Profiles")
    if not path.exists(profile_path):
        raise Exception("Firefox profiles directory not found.")

    default_profiles = glob(path.join(profile_path, "*.default"))
    if not default_profiles:
        raise Exception("Default profile not found.")

    return default_profiles[0]


def get_current_user_id(page):
    page.goto("https://sysdig.bizneohr.com")
    time_xpath = "//a[contains(@class, 'menu-link')][contains(@data-active-link, 'time-attendance')]"
    return page.locator(time_xpath).get_attribute("href").split("/")[-1]


def add_expected_schedule_at_date_for_user(page, user_id, year, month, day):
    page.goto(f"https://sysdig.bizneohr.com/time-attendance/my-logs/{user_id}?year={year}&month={month}")
    page.reload()
    page.locator(f"//tr[@data-bulk-element='{day}']/td[@class='actions']").click()
    add_default_schedule_selector = f"//form[contains(@action, '={day}')]//button[contains(@class, 'is-link')][contains(text(), 'jornada esperada')]"  # noqa
    if not any_locator_is_visible(page, add_default_schedule_selector):
        print("Schedule was already registered")
        return

    print(f"Adding expected schedule for user {user_id} at {year}-{month}-{day}")
    for element in page.locator(add_default_schedule_selector).all():
        if element.is_visible():
            element.click()
    page.locator("//button[contains(text(), 'Confirmar')]").click()
    page.wait_for_selector("//*[contains(text(), 'Has añadido con éxito')]").wait_for_element_state("visible")


def any_locator_is_visible(page, selector):
    return any([x.is_visible() for x in page.locator(selector).all()])
