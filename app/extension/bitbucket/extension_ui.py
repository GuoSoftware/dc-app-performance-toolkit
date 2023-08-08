import random

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import BITBUCKET_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    rnd_pr = random.choice(datasets["pull_requests"])

    project_key = rnd_pr[1]
    repo_slug = rnd_pr[0]
    pull_request_id = rnd_pr[2]

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_logout action

    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = LoginPage(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.submit_login()
    #         get_started_page = GetStarted(webdriver)
    #         get_started_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:show_pr_squash_button")
        def sub_measure():
            page.go_to_url(
                f"{BITBUCKET_SETTINGS.server_url}/projects/{project_key}/repos/{repo_slug}/pull-requests/{pull_request_id}/overview")
            page.wait_until_visible(
                (By.CSS_SELECTOR, '.pull-request-activities'))  # Wait for Pull Request activities is visible
            page.wait_until_visible((By.ID, 'prSquashButton'))  # Wait for you app-specific UI element by ID selector
        sub_measure()

        @print_timing("selenium_app_custom_action:open_pr_squash_dialog")
        def sub_measure():
            page.wait_until_clickable((By.ID, 'prSquashButton')).click()
            page.wait_until_clickable((By.ID, 'prSquashSubmit'))
        sub_measure()

        @print_timing("selenium_app_custom_action:perform_pr_squash_action")
        def sub_measure():
            select = page.select(page.get_element((By.ID, 'prSquashCommitAuthor')))
            select.select_by_visible_text('admin')
            page.get_element((By.ID, 'prSquashCommitMessage')).send_keys(page.generate_random_string(1))
            page.wait_until_clickable((By.ID, 'prSquashSubmit')).click()  # Submit the request
            try:
                page.wait_until_invisible((By.ID, 'prSquashSubmit')) # Expect the dialog with prSquashButton button to disppear after the PR page reload after the success
            except TimeoutException:  # We only catch the '409 Conflict' error due to a possible PR code change during the testing
                squash_status = page.get_element((By.ID, 'prSquashStatus'))
                error409_msg = "The pull request version has changed. Please confirm the changes before squashing the pull request."
                if error409_msg in squash_status.text:
                    page.get_element((By.ID, 'prSquashCancel')).click()
                else:
                    raise
        sub_measure()
    measure()
