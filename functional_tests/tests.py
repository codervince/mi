

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.test import Client, TestCase
import unittest

USER_NAME = 'tester1'
PASSWORD = 'pa$$w0rd'







class SignedUpUserTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_runners_table(self,row_text):
        table = self.browser.find_element_by_id('runnerstable')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])


    def dologin(self):
        self.browser.get('http://localhost:8000')
        # logged out
        navbar = self.browser.find_element_by_css_selector('.nav')

        self.assertIn('Login', navbar.text)
        # log in
        self.browser.find_element_by_css_selector("a[href*='login']").click()

        self.browser.find_element_by_id('id_username').send_keys(USER_NAME)
        self.browser.find_element_by_id('id_password').send_keys(PASSWORD)
        self.browser.find_element_by_name("login").click()



    def test_racecoursename_for_all_rows(self):
        #go to systems/systems
        self.dologin()
        self.browser.get('http://localhost:8000/systems/system/2016-MI-S-02A/')
        self.check_for_row_in_runners_table('Southwell (AW)')

    def test_welcome_page_for_visitor(self):

        #user anon sees welcome page at ('/')
        #User tester1 has logged in and returns to site.

        self.browser.get('http://localhost:8000/')
        #am I logged in?
        navbar = self.browser.find_element_by_css_selector('.nav')
        self.assertIn('Login', navbar.text)
        self.assertIn('Modern technology helps you track ', self.browser.find_element_by_tag_name('body').text)

    def test_login(self):

        self.browser.get('http://localhost:8000')
        # logged out
        navbar = self.browser.find_element_by_css_selector('.nav')

        self.assertIn('Login', navbar.text)
        # log in
        self.browser.find_element_by_css_selector("a[href*='login']").click()

        self.browser.find_element_by_id('id_username').send_keys(USER_NAME)
        self.browser.find_element_by_id('id_password').send_keys(PASSWORD)
        self.browser.find_element_by_name("login").click()

        self.assertIn('Logout', navbar.text)

    # def test_welcome_page_for_loggedin_user(self):
    #     # User tester1 has logged in and returns to home page.
    #     # is redirected to systems/systems
    #
    #     self.dologin()
    #     #go to home
    #     self.browser.get('http://localhost:8000/')
    #     self.assertEquals(response['location'], '/systems/systems/')






class VisitorSystemsTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.quit()

    def CanViewSystemPerformanceSummaryOnSystemsPage(self):

        #Bob hears about this site and wants to read more about it and look at how the systems
        # are currently performing

        self.driver.get('http://localhost:8000/systems/systems')
        '''
        http://selenium-python.readthedocs.org/api.html
        http://selenium-python.readthedocs.org/locating-elements.html
        possible asserts PY unittest and DJANGO
        assertEqual(a, b)	a == b
        assertNotEqual(a, b)	a != b
        assertTrue(x)	bool(x) is True
        assertFalse(x)	bool(x) is False
        assertIs(a, b)	a is b	2.7
        assertIsNot(a, b)	a is not b	2.7
        assertIsNone(x)	x is None	2.7
        assertIsNotNone(x)	x is not None	2.7
        assertIn(a, b)	a in b	2.7
        assertNotIn(a, b)	a not in b	2.7
        assertIsInstance(a, b)	isinstance(a, b)	2.7
        assertNotIsInstance(a, b)
        assert https://docs.python.org/2/library/unittest.html#assert-methods
        ID = "id"
        XPATH = "xpath"
        LINK_TEXT = "link text"
        PARTIAL_LINK_TEXT = "partial link text"
        NAME = "name"
        TAG_NAME = "tag name"
        CLASS_NAME = "class name"
        CSS_SELECTOR = "css selector"
        '''
        #He sees the Systems page
        self.assertIn('Systems Update', self.driver.title)

        #find a table with a particular system name in it or using django tables?
        table = self.driver.find_element_by_tag_name('table')
        rows = table.find_elements_by_tag_name('td')
        headers = table.find_elements_by_tag_name('th')
        self.assertTrue(
            any(row.text == '2016-S-01T' for row in rows),
            "System 2016-S-01T not in table:Check!"
        )
        fields_to_exclude= [ "ID", "snapshotid", "query", "rpquery", "updated", "created", "systemtype", "oddsconditions", "premium"]
        #does not see any ugly IDs, snapshotid, query, rpquery
        self.assertFalse(
            any(h.text in fields_to_exclude for h in headers),
        )
        snapshot_fields = [ "winsr", "bfwins", "bfruns", "a_e", "levelbsprofit"]
        # #displays current winsr, wins, runs
        # self.assertTrue(
        #     any(h.text in snapshot_fields for h in headers),
        #     "Please add snapshot fields to table!"
        # )

        ##should be able to link to system details page in table
        system_link = self.driver.find_element_by_link_text('2016-S-01T')
        self.assertIsNotNone(system_link)

        ##TODO: APR 21 well waiting to resolve this properly- is it a func or a unit test?

        #shiuld be able to access every susyem detail page - no dead links!
        ### put this in unit tests since selenium cant do status requests!!
        # alinks = self.driver.findElements(By.tagName("a"))
        # invalidLinksCount = 0;
        # for l in alinks:
        #     if l:
        #         url = l.get_attribute('href')
        #         if url:
        #             self.driver.get(url)
        #             self.
        #         else:
        #             invalidLinksCount+=1


        #isActive is a CSS attribute class="isActive" and hidden
        # find_element_by_css_selector(".span")
        # self.assertIsNone(self.driver.find_element_by_css_selector("td.isActive").get_attribute('display'))
        # self.driver.execute_script("document.getElementById('isActive').style.display='none'")

        # isActive = self.driver.find_element_by_xpath('//span[@class=isActive]').is_


        #TODO return to this later.


if __name__ == '__main__':
    unittest.main(warnings='ignore')