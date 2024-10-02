from typing import List
from os import path
from glob import glob
from playwright.sync_api import sync_playwright, TimeoutError


PROFILE_PATH = ""
CHROMIUM_MACOS_PROFILE_PATH = "~/Library/Application Support/Chromium"
CHROMIUM_LINUX_PROFILE_PATH = "~/.config/chromium"
CHROMIUM_LINUX_SNAP_PROFILE_PATH = "~/snap/chromium/common/chromium"
CHROMIUM_PATHS = [CHROMIUM_MACOS_PROFILE_PATH, CHROMIUM_LINUX_PROFILE_PATH, CHROMIUM_LINUX_SNAP_PROFILE_PATH]

FIREFOX_MACOS_PROFILE_PATH = "~/Library/Application Support/Firefox/Profiles"
FIREFOX_LINUX_PROFILE_PATH = "~/.mozilla/firefox"
FIREFOX_LINUX_SNAP_PROFILE_PATH = "~/snap/firefox/common/.mozilla/firefox/"
FIREFOX_PATHS = [FIREFOX_MACOS_PROFILE_PATH, FIREFOX_LINUX_PROFILE_PATH, FIREFOX_LINUX_SNAP_PROFILE_PATH]


def add_expected_schedule(date, headless, browser):
    with sync_playwright() as playwright:
        browser, page = get_browser_and_page(playwright, date, headless, browser)
        user_id = get_current_user_id(page)
        year, month, day = (date.year, date.month, date.day)
        add_expected_schedule_at_date_for_user(page, user_id, year, month, day)
        browser.close()


# Fixme(fede): should we refactor this and move it to another module?
def get_browser_and_page(playwright, date, headless, browser):
    if browser == "firefox":
        return get_firefox(playwright, date, headless)
    elif browser == "chromium":
        return get_chromium(playwright, date, headless)

    print(f"Warning: unsupported browser specified: {browser}, will fallback to firefox")
    return get_firefox(playwright, date, headless)


def get_firefox(playwright, date, headless):
    browser = playwright.firefox.launch_persistent_context(
        user_data_dir=PROFILE_PATH or _get_default_firefox_profile(),
        headless=headless,
        args=["--new-tab"],
    )
    page = browser.pages[0]
    return browser, page


def get_chromium(playwright, date, headless):
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH or _get_default_chromium_profile(),
        headless=headless,
    )
    return browser, browser.new_page()


def _profile_path(paths: List[str]) -> str:
    for profile_path in paths:
        profile_path = path.expanduser(profile_path)
        if path.exists(profile_path):
            return profile_path
    raise Exception("Profiles directory not found.")


def _get_default_firefox_profile():
    profile_path = _profile_path(FIREFOX_PATHS)
    default_profiles = glob(path.join(profile_path, "*.default"))
    if not default_profiles:
        raise Exception("Default profile not found.")

    return default_profiles[0]


def _get_default_chromium_profile():
    profile_path = _profile_path(CHROMIUM_PATHS)
    default_profiles = glob(path.join(profile_path, "Default"))
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
    ok = register_schedule(page, user_id, year, month, day)
    if not ok:
        return
    check_registration_was_ok(page, user_id, year, month, day)


def register_schedule(page, user_id, year, month, day):
    year_month_day = f"{year:04d}-{month:02d}-{day:02d}"
    page.locator(f"//tr[@data-bulk-element='{year_month_day}']/td[@class='actions']").click()
    add_default_schedule_selector = f"//form[contains(@action, '={year_month_day}')]//button[contains(@class, 'is-link')][contains(text(), 'jornada esperada')]"  # noqa
    if not any_locator_is_visible(page, add_default_schedule_selector):
        print("Schedule was already registered")
        return False

    for element in page.locator(add_default_schedule_selector).element_handles():
        if element.is_visible():
            element.click()

    page.locator("//button[contains(text(), 'Confirmar')]").click()

    return True


def check_registration_was_ok(page, user_id, year, month, day):
    try:
        ok_toast = page.wait_for_selector("//*[contains(text(), 'Has añadido con éxito')]", timeout=5000)
        ok_toast.wait_for_element_state("visible", timeout=3000)
        print(f"Added expected schedule for user {user_id} at {year}-{month:02d}-{day:02d}")
    except TimeoutError:
        ok_toast = page.wait_for_selector(
            "//*[contains(text(), 'No es posible registrar horas')]", timeout=5000
        )
        ok_toast.wait_for_element_state("visible", timeout=3000)
        print("Could not register schedule (probably you have an absence on that day)")


def any_locator_is_visible(page, selector):
    return any([x.is_visible() for x in page.locator(selector).element_handles()])
