from playwright.sync_api import Page
from utils.util import format_date_to_airbnb
from datetime import datetime


class HomePage:
    """
    This class represents the home page of the Airbnb website.
    """

    def __init__(self, page: Page, base_url):
        self.page = page
        self.base_url = base_url

    def goto(self):
        self.page.context.set_extra_http_headers({"Accept-Language": "en-US"})
        self.page.goto(self.base_url)

    # Locators

    def search_input(self):
        return self.page.get_by_test_id("structured-search-input-field-query")

    def date_button(self, date: datetime):
        date_str = format_date_to_airbnb(date)
        return self.page.get_by_role("button", name=date_str)

    def guests_button(self):
        return self.page.get_by_test_id("structured-search-input-field-guests-button")

    def adults_increase_button(self):
        return self.page.get_by_test_id("stepper-adults-increase-button")

    def adults_counter(self):
        return self.page.get_by_test_id("stepper-adults-value")

    def children_increase_button(self):
        return self.page.get_by_test_id("stepper-children-increase-button")

    def children_counter(self):
        return self.page.get_by_test_id("stepper-children-value")

    def search_button(self):
        return self.page.get_by_test_id("structured-search-input-search-button")

    # Actions

    def click_search_input(self):
        self.search_input().click()

    def fill_where(self, location):
        self.search_input().fill(location)

    def press_enter(self):
        self.search_input().press("Enter")

    def select_dates(self, check_in_date: datetime, check_out_date: datetime):
        check_in_button = self.date_button(check_in_date)
        check_out_button = self.date_button(check_out_date)
        check_in_button.click()
        check_out_button.click()

    def click_guests_button(self):
        self.guests_button().click()

    def click_add_adult(self):
        self.adults_increase_button().click()

    def click_add_child(self):
        self.children_increase_button().click()

    def add_num_of_adults(self, num_of_adults):
        for _ in range(num_of_adults):
            self.click_add_adult()

    def add_num_of_children(self, num_of_children):
        for _ in range(num_of_children):
            self.click_add_child()

    def click_search_button(self):
        self.search_button().click()

    def search_apartments(
        self,
        location: str,
        check_in_date: datetime,
        check_out_date: datetime,
        num_of_adults: int = 0,
        num_of_children: int = 0,
    ):
        # Search for an apartment in the specified location
        self.click_search_input()
        self.fill_where(location)
        self.press_enter()

        # Choose the check-in and check-out dates
        self.select_dates(check_in_date, check_out_date)

        # Select guests
        self.click_guests_button()

        # Add adult guests
        self.add_num_of_adults(num_of_adults)

        # Add child guests
        self.add_num_of_children(num_of_children)

        # Search for available apartments
        self.click_search_button()
