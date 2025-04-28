from playwright.sync_api import Page
from datetime import datetime
import logging
import re


class AptDetails:
    """
    Class representing the apartment details page on Airbnb,
    where the user can make a reservation.
    """

    def __init__(self, page: Page):
        self.page = page

    # Locators

    def close_translation_popup_button(self):
        return self.page.get_by_role("button", name="Close")

    def trip_dates(self):
        return self.page.get_by_role("button", name="Change dates;")

    def trip_guests(self):
        return self.page.get_by_role("button", name=re.compile(r"(\d+)\s+guests"))

    def total_price(self):
        # The regex is used to match the total price, that comes in a row like "Total ... X,XXX ..."

        return (
            self.page.locator("div")
            .filter(has_text=re.compile(r"^Total[^\d]*[\d,]*[^\d]*"))
            .first
        )

    def reserve_button(self):
        return self.page.get_by_role("button", name="Reserve")

    # Actions

    def click_close_translation_popup_button(self):
        """
        Attempt to click the close button on the translation popup if it appears.
        """

        try:
            self.close_translation_popup_button().click(timeout=5000)
        except Exception as e:
            # Don't raise an error if the button is not found or clickable
            logging.debug("Failed to close translation popup: %s", str(e))

    def get_dates(self) -> tuple[datetime, datetime]:
        """
        Gets the check-in and check-out dates from the apartment details page.

        Returns:
            tuple[datetime, datetime]: The check-in and check-out dates in datetime format.
        """

        dates_text = self.trip_dates().inner_text().split("\n")

        # The dates are in the format "month/day/year"
        check_in_date = dates_text[1]
        check_out_date = dates_text[3]

        # Convert the dates to datetime objects
        check_in_date_dt = datetime.strptime(check_in_date, "%m/%d/%Y")
        check_out_date_dt = datetime.strptime(check_out_date, "%m/%d/%Y")

        return check_in_date_dt, check_out_date_dt

    def get_number_of_guests(self):
        """
        Gets the number of guests from the apartment details page.

        Returns:
            int: The number of guests.

        Raises:
            ValueError: If the number of guests could not be found in the text.
        """

        guests_text = self.trip_guests().inner_text()
        guests_regex = r"GUESTS\s+(\d+)\s+guests"  # For example: "GUESTS 2 guests"

        match = re.search(guests_regex, guests_text)

        if match:
            number_of_guests = int(match.group(1))
        else:
            raise ValueError("Could not find the number of guests in the text.")

        return number_of_guests

    def get_total_price(self):
        """
        Gets the total price from the apartment details page.

        Returns:
            int: The total price.

        Raises:
            ValueError: If the total price could not be found in the text.
        """

        total_text = self.total_price().inner_text()
        total_regex = r"Total[^\d]*([\d,]*)[^\d]*"

        match = re.search(total_regex, total_text)

        if match:
            total_price = int(match.group(1).replace(",", ""))
        else:
            raise ValueError("Could not find the total price in the text.")

        return total_price

    def click_reserve_button(self):
        self.reserve_button().click()
