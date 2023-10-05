import unittest
from unittest.mock import patch, MagicMock

from backend.app.scraping import scrape_ind_organisations, IND_HEADER_1, IND_HEADER_2, \
    scrape_organization_linkedin_from_google


class TestScraping(unittest.TestCase):

    @patch('requests.get')
    def test_scrape_ind_organisations_expected_table_structure(self, mock_get):
        """Verify that the function preforms properly on the expected website table data."""
        expected_organisations = ['Company A', 'Company B']
        mock_url = "https://example.com"

        mock_response = MagicMock()
        mock_response.content = f'''
                <table><thead>
                    <tr><th scope="row">{IND_HEADER_1}</th>
                        <th scope="col">{IND_HEADER_2}</th></tr>
                    <tr><th scope="row"> Company A</th>
                        <th scope="col">24395334</th></tr>
                </thead><tbody><tr><th scope="row">Company B</th>
                        <td>17037842</td></tr>
                </tbody></table>
            '''
        mock_get.return_value = mock_response

        returned_organisations = scrape_ind_organisations(mock_url)

        self.assertEqual(expected_organisations, returned_organisations)

    def test_scrape_ind_organisations(self):
        organisations = scrape_ind_organisations()
        self.assertTrue(len(organisations) > 100)
        self.assertTrue("ABB B.V." in organisations)
        print(f"{len(organisations)} organisations were scraped.")


class TestPaidScraping(unittest.TestCase):

    def test_scrape_organization_linkedin_from_google(self):
        linkedin = scrape_organization_linkedin_from_google("ABB B.V.")
        self.assertEqual("https://www.linkedin.com/company/abb", linkedin)
