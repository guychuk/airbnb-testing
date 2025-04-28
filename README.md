# Airbnb Testing Project

This project contains automated tests for Airbnb functionalities using Python and the `pytest` framework. Below are detailed instructions on how to install dependencies and run the tests.

---

## Table of Contents
- [Airbnb Testing Project](#airbnb-testing-project)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Tests](#running-the-tests)
  - [Configuration](#configuration)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python 3.8 or higher
- `pip` (Python package manager)

---

## Installation

1. **Set Up a Virtual Environment**:  
    Create and activate a virtual environment to isolate dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

2. **Clone the Repository**:
    ```bash
    git clone https://github.com/guychuk/airbnb-testing.git
    cd airbnb-testing
    ```

3. **Install Dependencies**:  
    Install [Playwright for Pytest](https://playwright.dev/python/docs/intro):
    ```bash
    pip install pytest-playwright
    ```

4. **Install Browsers**:
    ```bash
    playwright install
    ```

---

## Running the Tests

1. **Open the Project's Folder**:
   ```bash
   cd airbnb-testing
   ```

2. **Run the Tests**:  
    Use the `pytest` command to execute the tests:
    ```bash
    pytest
    ```
---

## Configuration

- **`pytest.ini`**: Contains pytest configurations (you choose browser to test there, default is chromium).
- **Fixtures**: Shared test setup defined in `conftest.py`.
