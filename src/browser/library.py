from typing import List
from os import path
from glob import glob
from playwright.sync_api import sync_playwright


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
        browser, page = get_browser_and_page(playwright, headless, browser)
        page.goto("https://sysdig.bizneohr.com")

        registered_locator = page.locator(
            '//div[@class="day-header today"]//following-sibling::div[@class="registered"]'
        )
        if registered_locator.count() > 0:
            print("Schedule already registered")
            return

        page.locator(f'//span[@hx-indicator="#spinner-day-{date.day}"]').click()
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
