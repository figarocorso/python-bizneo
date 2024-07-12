import argparse
from os import path
from glob import glob
from datetime import datetime
from playwright.sync_api import sync_playwright


PROFILE_PATH = ""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=False, help="Fecha en formato YYYY-M-D (Default: today)")
    parser.add_argument("--headless", action="store_true", help="Run browswer in headless mode")
    args = parser.parse_args()
    if args.date:
        args.date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        args.date = datetime.now()
    return args


def get_default_firefox_profile():
    profile_path = path.expanduser("~/Library/Application Support/Firefox/Profiles")
    if not path.exists(profile_path):
        raise Exception("Firefox profiles directory not found.")

    default_profiles = glob(path.join(profile_path, "*.default"))
    if not default_profiles:
        raise Exception("Default profile not found.")

    return default_profiles[0]


def main(args):
    with sync_playwright() as p:
        firefox = p.firefox
        browser = firefox.launch_persistent_context(
            user_data_dir=PROFILE_PATH or get_default_firefox_profile(),
            headless=args.headless,
            args=["--new-tab"],
        )
        page = browser.pages[0]
        page.goto("https://sysdig.bizneohr.com")
        time_xpath = "//a[contains(@class, 'menu-link')][contains(@data-active-link, 'time-attendance')]"
        user_id = page.locator(time_xpath).get_attribute("href").split("/")[-1]
        year = args.date.year
        month = args.date.month
        day = args.date.day
        print(f"Adding expected schedule for user {user_id} at {year}-{month}-{day})")
        page.goto(f"https://sysdig.bizneohr.com/time-attendance/my-logs/{user_id}?year={year}&month={month}")
        page.reload()
        page.locator(f"//tr[@data-bulk-element='{day}']/td[@class='actions']").click()
        locator = page.locator(
            f"//form[contains(@action, '={day}')]//button[contains(@class, 'is-link')][contains(text(), 'Añadir jornada esperada')]"  # noqa
        )
        for element in locator.all():
            if element.is_visible():
                element.click()
        page.locator("//button[contains(text(), 'Confirmar')]").click()
        page.wait_for_selector("//*[contains(text(), 'Has añadido con éxito')]").wait_for_element_state(
            "visible"
        )
        browser.close()


if __name__ == "__main__":
    args = parse_args()
    main(args)
