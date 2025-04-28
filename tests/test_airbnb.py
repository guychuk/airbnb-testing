from pages.home_page import HomePage
from pages.search_results import SearchResultsPage
from pages.apt_details import AptDetails
from pages.reservation_page import ReservationPage
from datetime import datetime
import logging
from utils.util import format_date_to_airbnb


def test_search(page, base_url):
    """
    Searches for apartments in a certain place, with a certain number of adult guests,
    and verifies the search results.
    """

    home_page = HomePage(page, base_url)

    # Define search parameters
    location = "Tel Aviv"
    check_in_date = datetime(2025, 5, 1)
    check_out_date = datetime(2025, 5, 3)
    num_of_adults = 2

    # Go to the home page
    logging.info("1. Navigating to Airbnb website...")
    home_page.goto()

    # Search for apartments and get the search results page
    logging.info(
        f"2. Searching apartments for {num_of_adults} adults in {location} with check-in: {check_in_date} and check-out: {check_out_date}"
    )
    home_page.search_apartments(location, check_in_date, check_out_date, num_of_adults)

    # Verify the search results page
    logging.info("3. Verifying search results...")
    search_results_page = SearchResultsPage(home_page.page)
    search_results_page.verify_results(
        location, check_in_date, check_out_date, num_of_adults
    )

    # Find the highest rated apartment
    logging.info("4. Analyzing search results...")

    rating, text, _ = search_results_page.find_highest_rated(click=False)
    logging.info("a. Highest Rated Apartment:")
    logging.info(f"Highest Rating:   {rating}")
    logging.info(f"Apt. Details:     {text}")

    price, text, _ = search_results_page.find_cheapest(click=False)
    logging.info("b. Cheapest Apartment:")
    logging.info(f"Cheapest Price:   {price}")
    logging.info(f"Apt. Details:     {text}")


def test_reservation(page, base_url):
    """
    Searches for apartments in a certain place, with a certain number of guests,
    then try to make a reservation.
    """

    home_page = HomePage(page, base_url)

    # Define search parameters
    location = "Tel Aviv"
    check_in_date = datetime(2025, 5, 1)
    check_out_date = datetime(2025, 5, 5)
    num_of_adults = 2
    num_of_children = 1

    # Go to the home page
    logging.info("1. Navigating to Airbnb website...")
    home_page.goto()

    # Search for apartments
    logging.info(
        f"2. Searching apartments for {num_of_adults} adults and {num_of_children} children in {location} with check-in: {check_in_date} and check-out: {check_out_date}"
    )
    home_page.search_apartments(
        location, check_in_date, check_out_date, num_of_adults, num_of_children
    )

    # Verify the search results page
    logging.info("3. Verifying search results...")
    search_results_page = SearchResultsPage(home_page.page)
    search_results_page.verify_results(
        location, check_in_date, check_out_date, num_of_adults + num_of_children
    )

    # Find the highest rated apartment and click on it
    logging.info("4. Selecting highest rated apartment...")
    _, _, new_page = search_results_page.find_highest_rated(click=True)

    details_page = AptDetails(new_page)

    # Sometimes the translation popup appears, so we need to close it
    details_page.click_close_translation_popup_button()

    # Save reservation details
    logging.info("5a. Saving reservation details...")

    # Dates
    dates = details_page.get_dates()
    checkin_dt, checkout_dt = dates
    checkin_str = format_date_to_airbnb(checkin_dt)
    checkout_str = format_date_to_airbnb(checkout_dt)

    # Guests
    guests = details_page.get_number_of_guests()

    # Price
    price = details_page.get_total_price()

    # Print the reservation details
    logging.info("5b. Printing reservation details...")
    logging.info(f"Dates: {checkin_str} - {checkout_str}")
    logging.info(f"Number of guests: {guests}")
    logging.info(f"Total price: {price}")  # print(price_text)

    # Now make a reservation
    logging.info("6. Making a reservation...")

    logging.info("a. Clicking on the 'Reserve' button...")
    details_page.click_reserve_button()

    reservation_page = ReservationPage(new_page)

    # Verify that the data is correct
    logging.info("b. Verifying reservation details...")

    reservation_page.verify_reservation(
        num_of_adults, num_of_children, check_in_date, check_out_date
    )

    # Add phone number
    logging.info("c. Adding phone number...")
    reservation_page.signup_with_phone("054-1234567")
