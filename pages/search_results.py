from playwright.sync_api import Page, expect
from datetime import datetime
from utils.util import format_date_to_airbnb
import logging
import re
from conftest import CARD_LOAD_TIMEOUT
from utils.util import parse_dates

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

    def results_guests(self):
        return self.page.get_by_test_id("little-search-guests")

    def next_page_button(self):
        return self.page.get_by_role("link", name="Next")

    def previous_page_button(self):
        return self.page.get_by_role("link", name="Previous")

    def first_page_button(self):
        return self.page.get_by_role("link", name="1", exact=True)

    def cards_locator(self):
        return self.page.locator('div[itemprop="itemListElement"]')

    # Actions
    def click_results_dates(self):
        self.results_dates().click()

    def click_next_page(self):
        self.next_page_button().click()

    def click_previous_page(self):
        self.previous_page_button().click()

    def go_back_n_pages(self, n):
        for _ in range(n):
            if self.previous_page_button().is_enabled():
                self.click_previous_page()
            else:
                logging.info("No more previous pages to go back to.")
                break

    def go_back_to_first_page(self):
        self.first_page_button().click()

    def get_card_rating(self, card) -> float | int:
        """
        Extracts the rating from a card element.

        Args:
            card: The card element containing the rating information.

        Returns:
            float: The extracted rating as a float if found, otherwise -1.
        """

        rating_regex = re.compile(r"(\d\.\d+) out of 5 average rating")

        # Check if it has a rating
        match_rating = re.search(rating_regex, card.inner_text())

        if match_rating:
            rating = float(match_rating.group(1))

            return rating

        return -1

    def find_card_by_rating(self, target):
        card_index = 0

        while True:
            try:
                card = self.cards_locator().nth(card_index)
                card.wait_for(state="visible", timeout=CARD_LOAD_TIMEOUT)

                rating = self.get_card_rating(card)

                if rating == target:
                    return card

                card_index += 1
            except Exception as e:
                break

        return None

    def find_card_by_price(self, target):
        card_index = 0

        while True:
            try:
                card = self.cards_locator().nth(card_index)
                card.wait_for(state="visible", timeout=CARD_LOAD_TIMEOUT)

                price = self.get_card_price(card)

                if price == target:
                    return card

                card_index += 1
            except Exception as e:
                break

        return None

    def get_max_card_rating_in_page(self) -> tuple[float | int, int]:
        """
        Finds the highest rated card in the page.

        Returns:
            tuple: A tuple containing the highes rating in the page, and the total number of cards in the page.
        """

        card_index = 0
        highest_rating = -1

        while True:
            try:
                card = self.cards_locator().nth(card_index)
                card.wait_for(state="visible", timeout=CARD_LOAD_TIMEOUT)

                rating = self.get_card_rating(card)

                if rating > highest_rating:
                    highest_rating = rating

                card_index += 1
            except Exception as e:
                break

        return highest_rating, card_index

    def get_card_price(self, card) -> float:
        """
        Extracts the price from a card element.

        Args:
            card: The card element containing the rating information.

        Returns:
            float: The extracted price as a float if found, otherwise infinity.
        """

        # The line in which the price is displayed
        price_line_regex = re.compile(r"([^\n]+)\n(?=Show price breakdown)")

        # The price itself
        price_regex = re.compile(r"[^\d]*(\d[\d,\.]*)")

        # Get the price line
        match_price_line = re.search(price_line_regex, card.inner_text())

        if match_price_line:
            # Extract the price from the line
            match_price = re.search(price_regex, match_price_line.group(1))

            if match_price:
                # Convert the price to a float
                price = float(match_price.group(1).replace(",", ""))

                return price

        return float("inf")

    def get_min_card_price_in_page(self) -> tuple[float | int, int]:
        """
        Finds the cheapest card in the page.

        Returns:
            tuple: A tuple containing the lowest price in the page, and the total number of cards in the page.
        """

        card_index = 0
        lowest_price = float("inf")

        while True:
            try:
                card = self.cards_locator().nth(card_index)
                card.wait_for(state="visible", timeout=CARD_LOAD_TIMEOUT)

                price = self.get_card_price(card)

                if price < lowest_price:
                    lowest_price = price

                card_index += 1
            except Exception as e:
                break

        return lowest_price, card_index

    def find_highest_rated(
        self, click: bool = False
    ) -> tuple[int | float, str, Page | None]:
        """
        Finds the highest rated apartment on Airbnb.

        Args:
            click (bool, optional): If True, the function will click on the highest rated apartment and open its details page.

        Returns:
            tuple: A tuple containing the highest rated apartment's details (rating, description) and the new page (when not clicking this is None).
        """

        highest_rating = 0
        highest_rating_page = 0

        # Go back to the first page (if not already on it)
        if self.first_page_button().is_enabled():
            self.go_back_to_first_page()
        page_index = 1

        # Loop through the pages until there are no more pages
        while True and page_index:
            # Get the best card in the page
            highest_rating_in_page, num_of_cards = self.get_max_card_rating_in_page()

            # If the rating in the page is higher than the highest rating, update the highest rating
            if highest_rating_in_page > highest_rating:
                highest_rating = highest_rating_in_page
                highest_rating_page = page_index

            logging.debug(f"Done page {page_index}, read {num_of_cards} cards.")

            # If there are more pages, go to the next page
            if self.next_page_button().is_enabled() and page_index:
                self.click_next_page()
                page_index += 1
            else:
                break

        # Now go back to the page with the highest rating
        self.go_back_n_pages(page_index - highest_rating_page)

        # Get the card with the highest rating
        best_card = self.find_card_by_rating(highest_rating)

        if best_card is None:
            logging.error("No card with the highest rating was found.")
            raise ValueError("No card with the highest rating was found.")

        best_card_desc = best_card.inner_text()

        current_page = None

        if click:
            # Click on the card and open the details page
            with self.page.context.expect_page() as new_page_info:
                best_card.click()

            current_page = new_page_info.value

        return highest_rating, best_card_desc, current_page

    def find_cheapest(
        self, click: bool = False
    ) -> tuple[int | float, str, Page | None]:
        """
        Finds the cheapest apartment on Airbnb.

        Args:
            click (bool, optional): If True, the function will click on the cheapest apartment and open its details page.

        Returns:
            tuple: A tuple containing the cheapest apartment's details (price, description) and the new page (when not clicking this is None).
        """

        lowest_price = float("inf")
        lowest_price_page = 0

        # Go back to the first page (if not already on it)
        if self.first_page_button().is_enabled():
            self.go_back_to_first_page()
        page_index = 1

        # Loop through the pages until there are no more pages
        while True:
            # Get the best card in the page
            lowest_price_in_page, num_of_cards = self.get_min_card_price_in_page()

            # If the lowest price in the page is lower than the lowest price, update the lowest price
            if lowest_price_in_page < lowest_price:
                lowest_price = lowest_price_in_page
                lowest_price_page = page_index

            logging.debug(f"Done page {page_index}, read {num_of_cards} cards.")

            # If there are more pages, go to the next page
            if self.next_page_button().is_enabled():
                self.click_next_page()
                page_index += 1
            else:
                break

        # Now go back to the page with the lowest price
        self.go_back_n_pages(page_index - lowest_price_page)

        # Get the card with the lowest price
        best_card = self.find_card_by_price(lowest_price)

        if best_card is None:
            logging.error("No card with the lowest price was found.")
            raise ValueError("No card with the lowest price was found.")

        best_card_desc = best_card.inner_text()

        current_page = None

        if click:
            # Click on the card and open the details page
            with self.page.context.expect_page() as new_page_info:
                best_card.click()

            current_page = new_page_info.value

        return lowest_price, best_card_desc, current_page

    # Verification

    def verify_search_location(self, location):
        expect(self.results_location()).to_contain_text(location)

    def verify_results_heading_location(self, location):
        expect(self.results_heading_location()).to_contain_text(location)

    def verify_search_dates(self, check_in_date: datetime, check_out_date: datetime):
        self.results_dates().wait_for(state="visible")
        lines = self.results_dates().inner_text().split("\n")
        dates_text = lines[1]
        checkin, checkout = parse_dates(dates_text)

        assert checkin == check_in_date, "Check-in date does not match"
        assert checkout == check_out_date, "Check-out date does not match"

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
