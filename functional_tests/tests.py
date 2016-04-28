

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.test import Client, TestCase
from selenium.webdriver.common.by import By
from contextlib import contextmanager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

import unittest

USER_NAME = 'tester1'
PASSWORD = 'pa$$w0rd'

USER = {
    'username': 'Tester2',
    'firstname': 'TESTER2',
    'email': "wahwah@example.com",
    'password': "pa$$w0rd"

}

class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    @contextmanager
    def wait_for_page_load(self, timeout=30):
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, timeout).until(
            staleness_of(old_page)
        )




    # test offline then switch URL
    def test_can_see_subscription_and_start_up(self):

        # Abbot has read a tweet about a site and follow the link to the home page.
        self.browser.get('http://localhost:8000/')

        #he expects to see the welcome page..
        self.assertIn('Metainvest.io', self.browser.title)

        # He expected to see some text about the site
        # explanatory_text = "Statistical methods of handicapping"
        body_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Statistical methods of handicapping", body_text)

        # ...somewhere to read about how much it costs
        # Look for subscription panel
        subscription_info = self.browser.find_element_by_id("subscriptions")
        self.assertIn( 'Subscription Plans', subscription_info.text)

        # ...and a link to sign up
        # /account/registration/

        # He decides to sign up and is taken to a form
        # self.browser.find_element(By.PARTIAL_LINK_TEXT("registration")).click()
        self.browser.find_element_by_link_text("Sign up").click()


        # We were taken to the sign up page? Look for a form with a repeat password input 2
        # id_password2

        input_element= self.browser.find_element(By.XPATH, "//input[@id='id_password2']")
        self.assertIsNotNone(input_element)

        # He fills out the form with Username, firstname password
        signup_form = self.browser.find_element(By.TAG_NAME, "form")

        self.assertIsNotNone(signup_form)


        # first he fills out form and submits with no info. Expect validation error
        self.browser.find_element_by_name("submit").click()
        body_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("field is required", body_text)

        # Then he decides to do it properly

        username = self.browser.find_element_by_id("id_username")
        first_name = self.browser.find_element_by_id("id_first_name")
        email = self.browser.find_element_by_id("id_email")
        password = self.browser.find_element_by_id("id_password")
        password2 = self.browser.find_element_by_id("id_password2")

        username.send_keys(USER['username'])
        first_name.send_keys(USER['firstname'])
        email.send_keys(USER['email'])
        password.send_keys(USER['password'])
        password2.send_keys(USER['password'])
        self.browser.find_element_by_name("submit").click()

        body_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn("field is required", body_text)

        ## how else do we know that the form has been submitted properly?

        # After enter his details, he is signed in and taken to the systems/systems page

        #reffresh page?
        ##TODO: does not redirect!

        # with self.wait_for_page_load(timeout=30):
        #     ## what is on the systems/systems page?
        #
        #     self.assertEqual(self.browser.current_url, "http://localhost:8000/systems/systems")
        #
        #     h2_tags = self.browser.find_elements_by_tag_name('h2')
        #
        #     self.assertIn(
        #         any(tag.text== 'Season Performance' for tag in h2_tags)
        #     )


    def test_nonsignedinusers_cannot_see_systems_systems(self):

        # A visitor Val tries to go to systems/systems and is rediteced to the landing page

        self.browser.get('http://localhost:8000/systems/systems')

        self.assertNotEqual(self.browser.title, "Systems Page")

    def test_user_login_and_systemssystems_page(self):

        # User is logged in
        ## Assume USER is created
        # got to login page and sign in

        self.browser.get("http://metainvest.io/account/login/")

        username = self.browser.find_element_by_id("id_username")
        password = self.browser.find_element_by_id("id_password")

        username.send_keys(USER['username'])
        password.send_keys(USER['password'])

        #TODO: Why doesnt user log in?
        self.browser.find_element_by_name("login").click()

        # should now be on the right page
        self.browser.get('http://localhost:8000/systems/systems')

        print(self.browser.title)

        logout_link_text = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Logout")
        self.assertisNotNone(logout_link_text)

        # Billy should be logged in - look for a href /account/logout
        logout_tag = self.browser.find_element_by_xpath("//a[@href='/account/logout']")
        self.assertNotFalse(logout_tag)


        # He can view systems color coded based on viability = 3 factors


        self.assertEqual(self.browser.title, "Systems Page")

        # He sees all the systems currently active on this page


        # ALl the systems lead to the systems detail page


        # He chooses one SYSTEM =  and clicks the link



# def test_if_jquery_is_working(self):
    #
    #     element = self.browser.execute_script("return $('.row')[0]")



if __name__ == '__main__':
    unittest.main(warnings='ignore')








# On this System detail page, he can see 2016 stats


# On this page he can see 2015 stats including winsr, a-e and wins, runs and archie


# He fits subscribe but has no money and is taken to a Pay page


# On the pay page he can see bank details for offline payment


# on the pay page he can see a BTC QR Code for instant payment including the amount selected


# He chooses bank transfer by doing nothing.


# In 3 days he returns and is still logged in.


# Since he is logged in, he is taken to the systems/systems page first.

# Alternatvely he is logged in and is taken tot he day trader page


# He can see he has credit in one currency.


# He chooses the system he liked from before, seeing that the 2016 have been updated.


# He subscribes and money is taken out of his account.


# After subscribing he sees a confirmation of the subscription period.


# After subscribing he can see the extra information on the same systems/detail page id dayalerts


# AFter clicking subscribe he can see the new content day alerts right away







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