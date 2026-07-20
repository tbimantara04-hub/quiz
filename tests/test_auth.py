import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import string
import random
import os


class AuthTest(unittest.TestCase):
    """
    Testcase untuk modul Login dan Register menggunakan Selenium WebDriver.

    Stub/Driver yang digunakan:
    - Database MySQL XAMPP lokal sebagai stub untuk menyediakan data awal (user: ahmad/password123)
    - PHP built-in / Apache XAMPP sebagai stub server
    - WebDriver (ChromeDriver) sebagai driver pengujian antarmuka
    """

    BASE_URL = os.getenv("BASE_URL", "http://localhost/quiz-pengupil-main")

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        letters = string.ascii_lowercase
        self.rand_str = "".join(random.choice(letters) for i in range(8))

    def tearDown(self):
        self.driver.quit()

    # =========================================================
    # MODUL REGISTER
    # =========================================================

    def test_TC_REG_01_valid_data(self):
        """TC-REG-01: Registrasi dengan data valid → berhasil, redirect ke halaman lain"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys(f"Test User {self.rand_str}")
        driver.find_element(By.NAME, "email").send_keys(f"test_{self.rand_str}@example.com")
        driver.find_element(By.NAME, "username").send_keys(f"user_{self.rand_str}")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "repassword").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(2)
        # Verifikasi: halaman berpindah (tidak tetap di register.php)
        self.assertNotIn("register.php", driver.current_url,
                         "Seharusnya redirect setelah register sukses")

    def test_TC_REG_02_existing_username(self):
        """TC-REG-02: Registrasi dengan nama yang sudah terdaftar → muncul pesan error
        Catatan: fungsi cek_nama() di register.php mengecek field 'name' bukan 'username'.
        """
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys("irul")   # nama 'irul' sudah ada di DB
        driver.find_element(By.NAME, "email").send_keys(f"newmail_{self.rand_str}@example.com")
        driver.find_element(By.NAME, "username").send_keys(f"user_{self.rand_str}")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "repassword").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Username sudah terdaftar", error_msg.text,
                      "Seharusnya muncul pesan Username sudah terdaftar")

    def test_TC_REG_03_password_mismatch(self):
        """TC-REG-03: Registrasi dengan password & re-password tidak sama → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys(f"Test {self.rand_str}")
        driver.find_element(By.NAME, "email").send_keys(f"{self.rand_str}@example.com")
        driver.find_element(By.NAME, "username").send_keys(f"user_{self.rand_str}")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "repassword").send_keys("berbeda999")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        # Verifikasi: tetap di register.php dan muncul pesan error
        self.assertIn("register.php", driver.current_url,
                      "Seharusnya tetap di register.php jika password tidak sama")
        error_msg = driver.find_element(By.CLASS_NAME, "text-danger")
        self.assertIn("Password tidak sama", error_msg.text,
                      "Seharusnya muncul pesan Password tidak sama")

    def test_TC_REG_04_empty_fields(self):
        """TC-REG-04: Registrasi dengan semua field kosong → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text,
                      "Seharusnya muncul pesan Data tidak boleh kosong")

    def test_TC_REG_05_partial_empty_fields(self):
        """TC-REG-05: Registrasi dengan beberapa field kosong → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys("Hanya Nama")
        # email, username, password, repassword dibiarkan kosong
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text,
                      "Seharusnya muncul pesan Data tidak boleh kosong")

    def test_TC_REG_06_redirect_to_login(self):
        """TC-REG-06: Halaman register memiliki link menuju halaman login"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        login_link = driver.find_element(By.LINK_TEXT, "Login")
        self.assertIsNotNone(login_link, "Seharusnya ada link 'Login' di halaman register")
        login_link.click()
        time.sleep(1)
        self.assertIn("login.php", driver.current_url,
                      "Seharusnya berpindah ke halaman login.php")

    # =========================================================
    # MODUL LOGIN
    # =========================================================

    def test_TC_LOG_01_valid_credentials(self):
        """TC-LOG-01: Login dengan username & password yang valid → redirect sukses"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "username").send_keys("ahmad")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(2)
        # Verifikasi: tidak lagi berada di login.php
        self.assertNotIn("login.php", driver.current_url,
                         "Seharusnya redirect keluar dari login.php setelah login sukses")

    def test_TC_LOG_02_wrong_password(self):
        """TC-LOG-02: Login dengan password yang salah → tetap di login.php"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "username").send_keys("ahmad")
        driver.find_element(By.NAME, "password").send_keys("salah_password")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        self.assertIn("login.php", driver.current_url,
                      "Seharusnya tetap di login.php jika password salah")

    def test_TC_LOG_03_unregistered_username(self):
        """TC-LOG-03: Login dengan username tidak terdaftar → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "username").send_keys("user_tidak_ada_xyz")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Register User Gagal", error_msg.text,
                      "Seharusnya muncul pesan error saat username tidak ditemukan")

    def test_TC_LOG_04_empty_fields(self):
        """TC-LOG-04: Login dengan field kosong → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text,
                      "Seharusnya muncul pesan Data tidak boleh kosong")

    def test_TC_LOG_05_empty_username_only(self):
        """TC-LOG-05: Login dengan hanya password diisi → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text,
                      "Seharusnya muncul pesan Data tidak boleh kosong jika username kosong")

    def test_TC_LOG_06_redirect_to_register(self):
        """TC-LOG-06: Halaman login memiliki link menuju halaman register"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        register_link = driver.find_element(By.LINK_TEXT, "Register")
        self.assertIsNotNone(register_link, "Seharusnya ada link 'Register' di halaman login")
        register_link.click()
        time.sleep(1)
        self.assertIn("register.php", driver.current_url,
                      "Seharusnya berpindah ke halaman register.php")


if __name__ == "__main__":
    unittest.main(verbosity=2)
