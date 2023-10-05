from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

HTTP_OK = 200
IND_SPONSORS_URL = 'https://ind.nl/en/public-register-recognised-sponsors/public-register-regular-labour-and-highly-skilled-migrants'
IND_HEADER_1 = 'Company/organisation'
IND_HEADER_2 = 'Comp.Reg.nr.'


def scrape_ind_organisations(ind_sponsors_url: str = IND_SPONSORS_URL, ind_header_1: str = IND_HEADER_1,
                             ind_header_2: str = IND_HEADER_2) -> list:
    """
    Scrape the list of organisations from the IND sponsor URL.

    :param ind_sponsors_url: The URL of the IND sponsors page.
    :param ind_header_1: Header to be ignored during scraping. The text changes occasionally.
    :param ind_header_2: Another header to be ignored. The text changes occasionally.
    :return: A list of scraped organizations.
    """

    response = requests.get(ind_sponsors_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    organisation_elements = soup.select('th[scope=row]')
    organisations = [element.get_text(strip=True) for element in organisation_elements
                     if element.get_text(strip=True) not in [IND_HEADER_1, IND_HEADER_2]]

    return organisations


def scrape_organization_linkedin_from_google(organization: str):
    """
    Using the Custom Search JSON API for a programmable search engine that's set up to search only
    www.linkedin.com/* and nl.linkedin.com/*, search an organization of interest to find its company page.

    Note: With the free trials costs will be incurred upon more than 10,000 searches per day.
    # todo: add mechanism to track number of times the search is used between execution and tests;
        give warning when approaching 10k.

    :param organization: The search query.
    """
    secret_file_path = Path(__file__).resolve().parent.parent.parent / "secret.yaml"
    base_url = "https://www.googleapis.com/customsearch/v1"

    params = load_secret_keys(secret_file_path)
    params["q"] = organization

    response = requests.get(base_url, params=params)

    if response.status_code == HTTP_OK:
        data = response.json()
        if "items" in data:
            first_result = data["items"][0]
            return first_result["link"]
        else:
            return "No results found."
    else:
        print(response.text)  # todo: log
        raise RuntimeError("Error: Unable to retrieve search results.")


def load_secret_keys(file_path):
    """
    Load secret Google API key and programmable search engine (cx) ID from a YAML file.
    Note: Keep your personal secret file local on your computer, do NOT make it available online!

    :param file_path: The path to the YAML file containing the secret information.
    """
    with open(file_path, 'r') as secret_file:
        data = yaml.safe_load(secret_file)

    return {
        "key": data.get("my_key"),
        "cx": data.get("my_cx"),
    }
