import re
from playwright.sync_api import Page, Locator
from utils.util import parse_dates, parse_guests


class ReservationPage:
    def __init__(self, page: Page):
        self.page = page

    # Locators

    def continue_button(self):
        return self.page.get_by_role("button", name="Continue")

    def phone_number_input(self) -> Locator:
        return self.page.get_by_test_id("login-signup-phonenumber")

    def left_dates_locator(self):
        return self.page.get_by_text(re.compile(r"Dates.*Edit"))

    def left_guests_locator(self):
        return self.page.get_by_text(re.compile(r"Guests.*Edit"))

    def reservation_summary(self):
        return self.page.get_by_text(re.compile(r"Trip details.*Change"))

    # Actions

    def click_continue_button(self):
        self.continue_button().click()

    def fill_phone_number(self, phone_number):
        self.phone_number_input().fill(phone_number)

    def signup_with_phone(self, phone_number):
        # There are two kinds of reservation pages:
        # 1. The one with the "Continue" button to the left, that when clicked asks for phone number
        # 2. The one with the "Continue" button at the bottom, alreasy displaying phone number input
        if not self.phone_number_input().is_visible():
            self.click_continue_button()
            self.phone_number_input().wait_for(state="visible")

        self.fill_phone_number(phone_number)

    def header(self):
        return self.page.get_by_role(
            "heading", name=re.compile("Request to book|Confirm and pay")
        )

    # Validations

    def verify_reservation(self, exp_adults, exp_children, exp_check_in, exp_check_out):
        """
        Verifies the reservation summary page.

        Args:
            exp_adults (int): The expected number of adults.
            exp_children (int): The expected number of children.
            exp_check_in (datetime): The expected check-in date.
            exp_check_out (datetime): The expected check-out date.
        """

        self.header().wait_for(state="visible")

        if (
            self.left_dates_locator().is_visible()
            and self.left_guests_locator().is_visible()
        ):
            guests_text = self.left_guests_locator().inner_text().split("\n")[1]
            dates_text = self.left_dates_locator().inner_text().split("\n")[1]
        else:
            summary_text = self.reservation_summary().inner_text()

            lines = summary_text.split("\n")

            dates_text = lines[1]
            guests_text = lines[2]

        # Assert dates
        chek_in_date, check_out_date = parse_dates(dates_text)
        assert chek_in_date == exp_check_in, "Mismatch in check-in date"
        assert check_out_date == exp_check_out, "Mismatch in checkout date"

        # Assert guests
        total_guests, adults, children = parse_guests(guests_text)
        if adults == -1 and children == -1:
            assert (
                total_guests == exp_adults + exp_children
            ), "Mismatch in total guests number"
        else:
            assert adults == exp_adults, "Mismatch in number of adults"
            assert children == exp_children, "Mismatch in number of children"
