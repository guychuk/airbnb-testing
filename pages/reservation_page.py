from playwright.sync_api import Page
from utils.util import parse_dates, parse_guests


class ReservationPage:
    def __init__(self, page: Page):
        self.page = page

    # Locators

    def continue_button(self):
        return self.page.get_by_role("button", name="Continue")

    def phone_number_input(self):
        return self.page.get_by_test_id("login-signup-phonenumber")

    def reservation_summary(self):
        return self.page.locator(".b1evnv76")

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
            self.page.wait_for_timeout(250)

        self.fill_phone_number(phone_number)

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

        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        if self.reservation_summary().is_visible():
            summary_text = self.reservation_summary().inner_text()

            lines = summary_text.split("\n")

            # fine the "Trip details" line index
            trip_details_index = lines.index("Trip details")

            dates = lines[trip_details_index + 1]
            guests = lines[trip_details_index + 2]
        else:
            fourth_div = self.page.locator("div:nth-child(4) > div > div > div").first

            # Check if it has "guests" in it
            if "guests" in fourth_div.inner_text():
                dates_div = self.page.locator(
                    "div:nth-child(3) > div > div > div"
                ).first
                guests_div = fourth_div
            else:
                dates_div = fourth_div
                guests_div = self.page.locator(
                    "div:nth-child(5) > div > div > div"
                ).first

            guests = guests_div.inner_text().split("\n")[1]
            dates = dates_div.inner_text().split("\n")[1]

        # Assert dates
        chek_in_date, check_out_date = parse_dates(dates)
        assert chek_in_date == exp_check_in, "Mismatch in check-in date"
        assert check_out_date == exp_check_out, "Mismatch in checkout date"

        # Assert guests
        total_guests, adults, children = parse_guests(guests)
        if adults == -1 and children == -1:
            assert (
                total_guests == exp_adults + exp_children
            ), "Mismatch in total guests number"
        else:
            assert adults == exp_adults, "Mismatch in number of adults"
            assert children == exp_children, "Mismatch in number of children"
