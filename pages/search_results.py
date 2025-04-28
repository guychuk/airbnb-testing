from playwright.sync_api import Page, expect
from datetime import datetime
from utils.util import format_date_to_airbnb
import logging
import re
import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


logging.basicConfig(level=logging.INFO)


class SearchResultsPage:
    """
    This class represents the search results page on Airbnb.
    """

    def __init__(self, page: Page):
        self.page = page

    # Locators
    def results_location(self):
        return self.page.get_by_test_id("little-search-location")

    def results_heading_location(self):
        return self.page.get_by_test_id("stays-page-heading")

    def results_dates(self):
        return self.page.get_by_test_id("little-search-anytime")

    def results_check_in(self):
        return self.page.get_by_test_id("structured-search-input-field-split-dates-0")

    def results_check_out(self):
        return self.page.get_by_test_id("structured-search-input-field-split-dates-1")

    def results_guests(self):
        return self.page.get_by_test_id("little-search-guests")

    def next_page_button(self):
        return self.page.get_by_role("link", name="Next")

    def previous_page_button(self):
        return self.page.get_by_role("link", name="Previous")

    def first_page_button(self):
        return self.page.get_by_role("link", name="1", exact=True)

    # Actions
    def click_results_dates(self):
        self.results_dates().click()

    def click_next_page(self):
        self.next_page_button().click()

    def click_previous_page(self):
        self.previous_page_button().click()

    def wait_for_search_results(self):
        """
        Waits for the search results to load by waiting for the first
        listing card and the footer to appear.

        Returns:
            bool: True if the search results loaded, False otherwise.
        """

        try:
            # Wait for the first listing card to appear
            self.page.wait_for_selector(
                'div[itemprop="itemListElement"]', timeout=30_000
            )

            # Wait for the footer to be visible
            self.page.wait_for_selector("footer", state="visible", timeout=20_000)

        except TimeoutError as e:
            logging.error(f"Timed out waiting for elements: {e}")
            pytest.fail(f"Timed out waiting for search results elements: {e}")

            return False
        return True

    def go_back_n_pages(self, n):
        for _ in range(n):
            if self.previous_page_button().is_enabled():
                self.click_previous_page()
            else:
                logging.info("No more previous pages to go back to.")
                break

    def go_back_to_first_page(self):
        self.first_page_button().click()

    def find_highest_rated(self, click: bool = False):
        """
        Finds the highest rated apartment on Airbnb.

        Args:
            click (bool, optional): If True, the function will click on the highest rated apartment and open its details page.

        Returns:
            tuple: A tuple containing the highest rating and the text of the card with the highest rating, if click is False.
                   Else, the function will return the details page of the highest rated apartment.
        """

        cards_selector = 'div[itemprop="itemListElement"]'
        rating_regex = re.compile(r"(\d\.\d) out of 5 average rating")

        highest_rating = 0
        highest_rating_page = 0
        rating_text = ""

        # Go back to the first page (if not already on it)
        if self.first_page_button().is_enabled():
            self.go_back_to_first_page()
        page_index = 1

        # Loop through the pages until there are no more pages
        while True:
            # Wait for all search results to load
            if not self.wait_for_search_results():
                logging.error("Failed to load search results")
                return

            cards = self.page.locator(cards_selector)

            # Search for the highest rating on the current page
            for card in cards.all():
                # Check if it has a rating
                match_rating = re.search(rating_regex, card.inner_text())

                if match_rating:
                    rating = float(match_rating.group(1))

                    # Update the highest rating and page index if found
                    if rating > highest_rating:
                        highest_rating = rating
                        highest_rating_page = page_index
                        rating_text = match_rating.group(0)

            if self.next_page_button().is_enabled():
                self.click_next_page()
                page_index += 1
            else:
                break

        # Now go back to the page with the highest rating
        self.go_back_n_pages(page_index - highest_rating_page)

        # Wait until all search results are loaded again
        if not self.wait_for_search_results():
            logging.error("Failed to load search results")
            return

        cards = self.page.locator(cards_selector)

        # Search for the card with the highest rating
        for card in cards.all():
            card_text = card.inner_text()

            match_rating = re.search(rating_text, card_text)

            # The first match is the one we want
            if match_rating:
                if click:
                    # Click on the card and open the details page
                    with self.page.context.expect_page() as new_page_info:
                        card.click()

                    return new_page_info.value
                else:
                    return highest_rating, card_text

        return None

    def find_cheapest(self, click: bool = False):
        """
        Finds the cheapest apartment on Airbnb.

        Args:
            click (bool, optional): If True, the function will click on the cheapest apartment and open its details page.

        Returns:
            tuple: A tuple containing the lowest price and the text of the card with the lowest price, if click is False.
                   Else, the function will return the details page of the cheapest apartment.
        """

        cards_selector = 'div[itemprop="itemListElement"]'

        # The line in which the price is displayed
        price_line_regex = re.compile(r"([^\n]+)\n(?=Show price breakdown)")

        # The price itself
        price_regex = re.compile(r"[^\d]*(\d[\d,\.]*)")

        lowest_price = float("inf")
        lowest_price_page = 0
        price_text = ""

        # Go back to the first page (if not already on it)
        if self.first_page_button().is_enabled():
            self.go_back_to_first_page()
        page_index = 1

        # Loop through the pages until there are no more pages
        while True:
            # Wait for all search results to load
            if not self.wait_for_search_results():
                logging.error("Failed to load search results")
                return

            cards = self.page.locator(cards_selector)

            # Search for the highest rating on the current page
            for card in cards.all():
                # Get the price line
                match_price_line = re.search(price_line_regex, card.inner_text())

                if match_price_line:
                    # Extract the price from the line
                    match_price = re.search(price_regex, match_price_line.group(1))

                    if match_price:
                        # Convert the price to a float
                        price = float(match_price.group(1).replace(",", ""))

                        if price < lowest_price:
                            lowest_price = price
                            lowest_price_page = page_index
                            price_text = match_price_line.group(0)

            if self.next_page_button().is_enabled():
                self.click_next_page()
                page_index += 1
            else:
                break

        # Now go back to the page with the highest rating
        self.go_back_n_pages(page_index - lowest_price_page)

        # Wait until all search results are loaded again
        if not self.wait_for_search_results():
            logging.error("Failed to load search results")
            return

        cards = self.page.locator(cards_selector)

        # Search for the card with the lowest price
        for card in cards.all():
            card_text = card.inner_text()
            match_price = re.search(price_text, card_text)

            # The first match is the one we want
            if match_price:
                if click:
                    # Click on the card and open the details page
                    with self.page.context.expect_page() as new_page_info:
                        card.click()

                        return new_page_info.value
                else:
                    return lowest_price, card_text

        return None

    # Verify
    def verify_search_location(self, location):
        expect(self.results_location()).to_contain_text(location)

    def verify_results_heading_location(self, location):
        expect(self.results_heading_location()).to_contain_text(location)

    def verify_search_dates(self, check_in_date: datetime, check_out_date: datetime):
        check_in_str = format_date_to_airbnb(check_in_date, verbose=False)
        check_out_str = format_date_to_airbnb(check_out_date, verbose=False)
        expect(self.results_check_in()).to_contain_text(check_in_str)
        expect(self.results_check_out()).to_contain_text(check_out_str)

    def verify_search_guests(self, num_of_adults):
        expect(self.results_guests()).to_contain_text(f"{num_of_adults} guests")

    def verify_results(self, location, check_in_date, check_out_date, num_of_adults):
        """
        Verifies that the search results page displays the correct location, dates, and number of guests.

        Args:
            location (str): The expected location of the search results.
            check_in_date (datetime): The expected check-in date.
            check_out_date (datetime): The expected check-out date.
            num_of_adults (int): The expected number of adult guests.
        """

        self.verify_search_location(location)
        self.verify_results_heading_location(location)
        self.verify_search_dates(check_in_date, check_out_date)
        self.verify_search_guests(num_of_adults)
