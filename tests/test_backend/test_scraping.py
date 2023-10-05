import unittest

from backend.app.scraping import scrape_ind_organisations, scrape_organization_linkedin_from_google


class TestScraping(unittest.TestCase):

    def test_scrape_ind_organisations(self):
        organisations = scrape_ind_organisations()
        self.assertTrue(len(organisations) > 100)
        self.assertTrue("ABB B.V." in organisations)
        print(f"{len(organisations)} organisations were scraped.")

    def test_scrape_organization_linkedin_from_google(self):
        linkedin = scrape_organization_linkedin_from_google("ABB B.V.")
        self.assertEqual("https://www.linkedin.com/company/abb", linkedin)
