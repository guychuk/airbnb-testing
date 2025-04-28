import pytest

CARD_LOAD_TIMEOUT = 5_000  # ms


@pytest.fixture(scope="session")
def base_url():
    return "https://www.airbnb.com/"
