import argparse
import time
import unittest

from selenium import webdriver
from selenium.webdriver.common import action_chains as ac
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC

DRIVERS = [
    (webdriver.Firefox, "Firefox"),
    (webdriver.Chrome, "Chrome"),
]

url = None

class FactorioCalculatorTest(unittest.TestCase):

    DRIVER = webdriver.Firefox

    def setUp(self):
        self.driver = self.DRIVER()

    def tearDown(self):
        self.driver.quit()

    def load_page(self):
        driver = self.driver
        driver.get(url)
        self.assertEqual("Factorio Calculator", driver.title)
        ui.WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "display_count"), "1")
        )

def child_count(element):
    return len(element.find_elements_by_xpath("./*"))

def element_has_children(element, count):
    def fn(driver):
        if child_count(element) == count:
            return element
        return False
    return fn

def element_height_is(element, height):
    def fn(driver):
        if element.get_property("clientHeight") == height:
            return element
        return False
    return fn

class Settings:
    def __init__(self, **kwargs):
        self.settings = kwargs

    def apply_settings(self, driver):
        if not self.settings:
            return
        button = driver.find_element_by_id("settings_button")
        button.click()
        
        if "min" in self.settings:
            dropdown = driver.find_element_by_xpath("//span[@id='minimum_assembler']/div")
            img = dropdown.find_element_by_xpath("./label[%s]/img" % self.settings["min"])
            chain = ac.ActionChains(driver)
            chain.move_to_element(dropdown)
            chain.click(img)
            chain.perform()
        
        button = driver.find_element_by_id("totals_button")
        button.click()

class Solution:
    def __init__(self, name, targets, results, settings=None):
        self.name = name
        self.targets = targets
        self.results = results
        if not settings:
            settings = Settings()
        self.settings = settings

    def test_solution(self, test, driver):
        test.load_page()
        self.settings.apply_settings(driver)
        self.set_targets(driver)
        self.verify_solution(test, driver)

    def set_targets(self, driver):
        driver.implicitly_wait(1)
        targets = driver.find_element_by_id("targets")
        for i, target in enumerate(self.targets, start=1):
            name, field, rate = target
            if i != 1:
                count = child_count(targets)
                add = targets.find_element_by_xpath("./li[last()]/button")
                add.click()
                ui.WebDriverWait(driver, 10).until(
                    element_has_children(targets, count + 1)
                )
            li = targets.find_element_by_xpath("./li[%d]" % i)
            x_button = li.find_element_by_xpath("./button")
            dropdown = li.find_element_by_xpath("./div[contains(@class, 'dropdown')]")
            img = dropdown.find_element_by_xpath("./label/img[@alt='%s']" % name)
            if field == "f":
                input = li.find_element_by_xpath("./input[1]")
            else:
                input = li.find_element_by_xpath("./input[2]")
            chain = ac.ActionChains(driver)
            chain.move_to_element(dropdown)
            chain.perform()
            ui.WebDriverWait(driver, 10).until(
                element_height_is(dropdown, 313),
            )
            driver.execute_script("arguments[0].scrollTop = arguments[1].offsetTop;", dropdown, img)
            chain = ac.ActionChains(driver)
            chain.click(img)
            chain.move_to_element(x_button)
            chain.perform()
            input.clear()
            input.send_keys(rate)
            input.send_keys(Keys.RETURN)

    def verify_solution(self, test, driver):
        totals = driver.find_element_by_id("totals")
        rows = totals.find_elements_by_xpath("./tr[position() > 1]")
        test.assertEqual(len(self.results), len(rows) - 1)
        for result, row in zip(self.results, rows):
            name, expected_rate = result
            img = row.find_element_by_xpath("./td[1]/img")
            rate = row.find_element_by_xpath("./td[2]/tt")
            test.assertEqual(img.get_attribute("alt"), name)
            test.assertEqual(rate.text.strip(), expected_rate)

CASES = [
    Solution(
        "Default",
        targets=[
            ('advanced-circuit', 'f', '1'),
        ],
        results=[
            ('advanced-circuit', '7.5'),
            ('electronic-circuit', '15'),
            ('iron-plate', '15'),
            ('iron-ore', '15'),
            ('plastic-bar', '15'),
            ('coal', '7.5'),
            ('copper-cable', '75'),
            ('copper-plate', '37.5'),
            ('copper-ore', '37.5'),
            ('heavy-oil', '16.667'),
            ('light-oil', '87.5'),
            ('petroleum-gas', '150'),
            ('water', '183.333'),
            ('crude-oil', '166.667'),
        ],
    ),
    Solution(
        "Oil",
        targets=[
            ('heavy-oil', 'r', '10'),
            ('petroleum-gas', 'r', '45'),
        ],
        results=[
            ('heavy-oil', '10'),
            ('light-oil', '23.462'),
            ('petroleum-gas', '45'),
            ('water', '42.692'),
            ('crude-oil', '58.974'),
        ],
    ),
    Solution(
        "Circuit",
        settings=Settings(min='3'),
        targets=[
            ('electronic-circuit', 'f', '1'),
        ],
        results=[
            ('electronic-circuit', '150'),
            ('iron-plate', '150'),
            ('iron-ore', '150'),
            ('copper-cable', '450'),
            ('copper-plate', '225'),
            ('copper-ore', '225'),
        ],
    ),
]

def test_solution(self):
    self.SOLUTION.test_solution(self, self.driver)

for driver, browser_name in DRIVERS:
    for case in CASES:
        name = "{driver}{name}Test".format(name=case.name, driver=browser_name)
        dct = {
            "DRIVER": driver,
            "SOLUTION": case,
            "test_solution": test_solution,
        }
        globals()[name] = type(name, (FactorioCalculatorTest,), dct)

def main():
    global url
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8001/calc.html")
    args = parser.parse_args()
    url = args.url

    unittest.main()

if __name__ == "__main__":
    main()
