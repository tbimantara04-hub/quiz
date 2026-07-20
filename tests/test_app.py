import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class AppTest(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8000')

    def test_01_register_empty_fields(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register.php")
        driver.find_element(By.NAME, "submit").click()
        
        # Check if error message exists
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong !!", error_msg.text)

    def test_02_register_success(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register.php")
        
        username = f"testuser_{int(time.time())}"
        
        driver.find_element(By.ID, "name").send_keys("Test Name")
        driver.find_element(By.ID, "InputEmail").send_keys(f"{username}@test.com")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "InputPassword").send_keys("password123")
        driver.find_element(By.ID, "InputRePassword").send_keys("password123")
        
        driver.find_element(By.NAME, "submit").click()
        
        # Should redirect to index.php
        WebDriverWait(driver, 5).until(EC.url_contains("index.php"))
        self.assertIn("index.php", driver.current_url)

    def test_03_login_empty_fields(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login.php")
        driver.find_element(By.NAME, "submit").click()
        
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong !!", error_msg.text)

    def test_04_login_invalid_credentials(self):
        driver = self.driver
        driver.get(f"{self.base_url}/login.php")
        
        driver.find_element(By.ID, "username").send_keys("invalid_user")
        driver.find_element(By.ID, "InputPassword").send_keys("wrong_password")
        
        driver.find_element(By.NAME, "submit").click()
        
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Register User Gagal !!", error_msg.text) # Match the exact error message in login.php

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
