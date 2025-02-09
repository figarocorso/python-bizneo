from typing import List
from os import path
from glob import glob
from playwright.sync_api import sync_playwright


PROFILE_PATH = ""
HOME_PATH = path.expanduser("~")
CHROMIUM_MACOS_PROFILE_PATH = f"{HOME_PATH}~/Library/Application Support/Chromium"
CHROMIUM_LINUX_PROFILE_PATH = f"{HOME_PATH}/.config/chromium"
CHROMIUM_LINUX_SNAP_PROFILE_PATH = f"{HOME_PATH}/snap/chromium/common/chromium"
CHROMIUM_PATHS = [CHROMIUM_MACOS_PROFILE_PATH, CHROMIUM_LINUX_PROFILE_PATH, CHROMIUM_LINUX_SNAP_PROFILE_PATH]

FIREFOX_MACOS_PROFILE_PATH = f"{HOME_PATH}/Library/Application Support/Firefox/Profiles"
FIREFOX_LINUX_PROFILE_PATH = f"{HOME_PATH}/.mozilla/firefox"
FIREFOX_LINUX_SNAP_PROFILE_PATH = f"{HOME_PATH}/snap/firefox/common/.mozilla/firefox/"
FIREFOX_PATHS = [FIREFOX_MACOS_PROFILE_PATH, FIREFOX_LINUX_PROFILE_PATH, FIREFOX_LINUX_SNAP_PROFILE_PATH]


def add_expected_schedule(headless, browser):
    with sync_playwright() as playwright:
        browser, page = get_browser_and_page(playwright, headless, browser)
        page.goto("https://sysdig.bizneohr.com")

        if page.locator('//p[text()="Log in with"]').count() > 0:
            print("User not logged in. Run bizneo browser login.")
            return

        today_locator = '//div[@class="day-header today"]'

        register_button = page.locator(today_locator + "//following-sibling::button")
        if register_button.count() == 0:
            print("Schedule already registered")
            return

        register_button.click()

        registered_locator = page.locator(today_locator + '//following-sibling::div[@class="registered"]')
        registered_locator.wait_for(state="visible")
        print("Schedule registered")

        browser.close()


def login_into(browser):
    with sync_playwright() as playwright:
        browser, page = get_browser_and_page(playwright, False, browser)
        page.goto("https://sysdig.bizneohr.com", timeout=0)

        # Wait for a specific element that indicates the user is logged in.
        # Waiting for the button with specific classes to confirm login.
        page.wait_for_selector(".button.is-link.current-user.dropdown-btn.no-arrow", timeout=0)
        print("User successfully logged in.")

        browser.close()


# Fixme(fede): should we refactor this and move it to another module?
def get_browser_and_page(playwright, headless, browser):
    if browser == "firefox":
        return get_firefox(playwright, headless)
    elif browser == "chromium":
        return get_chromium(playwright, headless)

    print(f"Warning: unsupported browser specified: {browser}, will fallback to firefox")
    return get_firefox(playwright, headless)


def get_firefox(playwright, headless):
    browser = playwright.firefox.launch_persistent_context(
        user_data_dir=PROFILE_PATH or _get_default_firefox_profile(),
        headless=headless,
        args=["--new-tab"],
    )
    page = browser.pages[0]
    return browser, page


def get_chromium(playwright, headless):
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH or _get_default_chromium_profile(),
        headless=headless,
    )
    return browser, browser.new_page()


def _profile_path(paths: List[str], glob_subpath: str, default_path: str) -> str:
    for profile_path in paths:
        profile_path = path.expanduser(profile_path)
        if profile_path := glob(path.join(profile_path, glob_subpath)):
            return profile_path[0]
    return default_path


def _get_default_firefox_profile():
    return _profile_path(FIREFOX_PATHS, "*.default", FIREFOX_LINUX_PROFILE_PATH)


def _get_default_chromium_profile():
    return _profile_path(CHROMIUM_PATHS, "Default", CHROMIUM_LINUX_PROFILE_PATH)
