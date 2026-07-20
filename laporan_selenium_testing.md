# Laporan Pengujian Selenium: Modul Login & Register
**Mata Kuliah:** Rekayasa Perangkat Lunak / Pengujian Perangkat Lunak  
**Repository GitHub:** https://github.com/tbimantara04-hub/quiz  
**Tanggal Pengujian:** 20 Juli 2026  
**Tools:** Python 3.12, Selenium WebDriver, Google ChromeDriver, XAMPP (Apache + MySQL)

---

## 1. Pendahuluan

Laporan ini mendokumentasikan proses pengujian otomatis menggunakan **Selenium WebDriver** terhadap dua modul pada aplikasi web **Quiz Pengupil**, yaitu:
1. **Modul Register** — proses pendaftaran akun baru
2. **Modul Login** — proses masuk ke dalam sistem

Pengujian dilakukan menggunakan metode **Black-Box Testing** dengan pendekatan **Automated UI Testing** menggunakan Selenium, serta diterapkan pada pipeline **CI/CD (Continuous Integration/Continuous Deployment)** menggunakan **GitHub Actions**.

---

## 2. Arsitektur Aplikasi yang Diuji

Aplikasi berbasis **PHP + MySQL** yang berjalan di atas **Apache (XAMPP)**:

```
quiz-pengupil-main/
├── login.php           ← Modul Login (yang diuji)
├── register.php        ← Modul Register (yang diuji)
├── koneksi.php         ← Koneksi database MySQL
├── index.php           ← Halaman utama setelah login
├── db/
│   └── quiz_pengupil.sql  ← Schema & data awal database
├── tests/
│   ├── test_app.py     ← Testcase dasar (4 testcase)
│   └── test_auth.py    ← Testcase lengkap (12 testcase)
└── .github/
    └── workflows/
        └── selenium-test.yml  ← Konfigurasi CI/CD GitHub Actions
```

---

## 3. Konsep Stub dan Driver

Dalam pengujian ini digunakan konsep **Stub** dan **Driver** sebagai berikut:

| Komponen | Jenis | Fungsi |
|---|---|---|
| **MySQL XAMPP + data awal** | **Stub** | Menyediakan data pengguna awal (user: `irul`, `ahmad`) agar modul Login dapat diuji tanpa harus mendaftar manual terlebih dahulu |
| **Apache XAMPP (localhost)** | **Stub** | Menjadi server HTTP pengganti production server, sehingga PHP dapat dieksekusi secara lokal |
| **ChromeDriver** | **Driver** | Mengemudikan browser Chrome secara otomatis; meniru aksi pengguna (klik, ketik, navigasi) |
| **Python `unittest`** | **Driver** | Framework yang mengatur urutan eksekusi testcase, menangani setup/teardown, dan melaporkan hasil |
| **GitHub Actions Runner** | **Driver** | Menjalankan seluruh rangkaian pengujian secara otomatis di cloud setiap kali ada push ke branch `main` |

---

## 4. Kemungkinan Testcase

### 4.1 Modul Register

| No | Kode TC | Skenario | Input | Expected Output |
|---|---|---|---|---|
| 1 | TC-REG-01 | Registrasi dengan data lengkap & valid | Nama, email, username, password, repassword diisi benar | Redirect ke halaman lain (bukan register.php) |
| 2 | TC-REG-02 | Registrasi dengan nama yang sudah terdaftar | Nama `irul` (sudah ada di DB) | Muncul alert `Username sudah terdaftar !!` |
| 3 | TC-REG-03 | Registrasi dengan password & re-password tidak sama | Password: `password123`, Re-password: `berbeda999` | Muncul pesan `Password tidak sama !!` |
| 4 | TC-REG-04 | Registrasi dengan semua field kosong | Semua field dikosongkan | Muncul alert `Data tidak boleh kosong !!` |
| 5 | TC-REG-05 | Registrasi dengan sebagian field kosong | Hanya nama diisi | Muncul alert `Data tidak boleh kosong !!` |
| 6 | TC-REG-06 | Navigasi dari Register ke Login | Klik link "Login" di halaman register | Berpindah ke `login.php` |

### 4.2 Modul Login

| No | Kode TC | Skenario | Input | Expected Output |
|---|---|---|---|---|
| 7 | TC-LOG-01 | Login dengan kredensial valid | Username: `ahmad`, Password: `password123` | Redirect keluar dari `login.php` (login berhasil) |
| 8 | TC-LOG-02 | Login dengan password yang salah | Username: `ahmad`, Password: `salah_password` | Tetap di `login.php` |
| 9 | TC-LOG-03 | Login dengan username tidak terdaftar | Username: `user_tidak_ada_xyz` | Muncul alert `Register User Gagal !!` |
| 10 | TC-LOG-04 | Login dengan semua field kosong | Semua field dikosongkan | Muncul alert `Data tidak boleh kosong !!` |
| 11 | TC-LOG-05 | Login hanya mengisi field password | Username kosong, Password: `password123` | Muncul alert `Data tidak boleh kosong !!` |
| 12 | TC-LOG-06 | Navigasi dari Login ke Register | Klik link "Register" di halaman login | Berpindah ke `register.php` |

---

## 5. Script Selenium

### 5.1 `tests/test_app.py` — Testcase Dasar (4 Testcase)

```python
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
        self.base_url = os.getenv('BASE_URL', 'http://localhost/quiz-pengupil-main')

    def test_01_register_empty_fields(self):
        driver = self.driver
        driver.get(f"{self.base_url}/register.php")
        driver.find_element(By.NAME, "submit").click()
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
        self.assertIn("Register User Gagal !!", error_msg.text)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
```

---

### 5.2 `tests/test_auth.py` — Testcase Lengkap (12 Testcase)

```python
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

    # --- MODUL REGISTER ---

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
        self.assertNotIn("register.php", driver.current_url)

    def test_TC_REG_02_existing_username(self):
        """TC-REG-02: Registrasi dengan nama yang sudah terdaftar → muncul pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys("irul")  # nama 'irul' sudah ada di DB
        driver.find_element(By.NAME, "email").send_keys(f"newmail_{self.rand_str}@example.com")
        driver.find_element(By.NAME, "username").send_keys(f"user_{self.rand_str}")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "repassword").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Username sudah terdaftar", error_msg.text)

    def test_TC_REG_03_password_mismatch(self):
        """TC-REG-03: Registrasi dengan password & re-password tidak sama → pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys(f"Test {self.rand_str}")
        driver.find_element(By.NAME, "email").send_keys(f"{self.rand_str}@example.com")
        driver.find_element(By.NAME, "username").send_keys(f"user_{self.rand_str}")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "repassword").send_keys("berbeda999")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        self.assertIn("register.php", driver.current_url)
        error_msg = driver.find_element(By.CLASS_NAME, "text-danger")
        self.assertIn("Password tidak sama", error_msg.text)

    def test_TC_REG_04_empty_fields(self):
        """TC-REG-04: Registrasi dengan semua field kosong → pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text)

    def test_TC_REG_05_partial_empty_fields(self):
        """TC-REG-05: Registrasi dengan beberapa field kosong → pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        driver.find_element(By.NAME, "name").send_keys("Hanya Nama")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text)

    def test_TC_REG_06_redirect_to_login(self):
        """TC-REG-06: Halaman register memiliki link menuju halaman login"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/register.php")
        login_link = driver.find_element(By.LINK_TEXT, "Login")
        login_link.click()
        time.sleep(1)
        self.assertIn("login.php", driver.current_url)

    # --- MODUL LOGIN ---

    def test_TC_LOG_01_valid_credentials(self):
        """TC-LOG-01: Login dengan username & password valid → redirect sukses"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "username").send_keys("ahmad")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(2)
        self.assertNotIn("login.php", driver.current_url)

    def test_TC_LOG_02_wrong_password(self):
        """TC-LOG-02: Login dengan password yang salah → tetap di login.php"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "username").send_keys("ahmad")
        driver.find_element(By.NAME, "password").send_keys("salah_password")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        self.assertIn("login.php", driver.current_url)

    def test_TC_LOG_03_unregistered_username(self):
        """TC-LOG-03: Login dengan username tidak terdaftar → pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "username").send_keys("user_tidak_ada_xyz")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Register User Gagal", error_msg.text)

    def test_TC_LOG_04_empty_fields(self):
        """TC-LOG-04: Login dengan field kosong → pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text)

    def test_TC_LOG_05_empty_username_only(self):
        """TC-LOG-05: Login dengan hanya password diisi → pesan error"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.NAME, "submit").click()
        time.sleep(1)
        error_msg = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Data tidak boleh kosong", error_msg.text)

    def test_TC_LOG_06_redirect_to_register(self):
        """TC-LOG-06: Halaman login memiliki link menuju halaman register"""
        driver = self.driver
        driver.get(f"{self.BASE_URL}/login.php")
        register_link = driver.find_element(By.LINK_TEXT, "Register")
        register_link.click()
        time.sleep(1)
        self.assertIn("register.php", driver.current_url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

---

## 6. Konfigurasi CI/CD GitHub Actions

File: `.github/workflows/selenium-test.yml`

```yaml
name: Selenium Tests

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:5.7
        env:
          MYSQL_ALLOW_EMPTY_PASSWORD: "yes"
          MYSQL_DATABASE: quiz_pengupil
        ports:
          - "3306:3306"

    steps:
    - uses: actions/checkout@v3

    - name: Set up PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.1'
        extensions: mysqli, pdo_mysql

    - name: Wait for MySQL to be ready
      run: |
        until mysqladmin ping -h 127.0.0.1 --silent; do
          echo "Waiting for MySQL database to start..."
          sleep 3
        done

    - name: Import Database
      run: |
        mysql -h 127.0.0.1 -u root quiz_pengupil < db/quiz_pengupil.sql
        # Update password user 'ahmad' ke 'password123' agar sesuai dengan testcase
        mysql -h 127.0.0.1 -u root quiz_pengupil -e \
          "UPDATE users SET password='\$2y\$10\$25SITQTDZvTioM.TT65IXedugTtFeUNFnXJCAk/LK9VA93ItXCvvq' WHERE username='ahmad';"

    - name: Start PHP Server
      run: |
        php -S localhost:8000 &
        sleep 3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install selenium

    - name: Run Selenium Tests
      env:
        BASE_URL: http://localhost:8000
      run: |
        echo "=== Running test_app.py ==="
        python tests/test_app.py
        echo "=== Running test_auth.py ==="
        python tests/test_auth.py
```

---

## 7. Hasil Pengujian

### 7.1 Hasil `test_app.py` (Pengujian Lokal)

**Perintah:** `python test_app.py`  
**Durasi:** ~16 detik  
**Environment:** Windows, XAMPP Apache, MySQL, ChromeDriver

```
....
----------------------------------------------------------------------
Ran 4 tests in 16.321s

OK
```

| No | Nama Test | Deskripsi Skenario | Status |
|---|---|---|:---:|
| 1 | `test_01_register_empty_fields` | Register dengan semua field kosong → error | ✅ PASS |
| 2 | `test_02_register_success` | Register dengan data valid → redirect index.php | ✅ PASS |
| 3 | `test_03_login_empty_fields` | Login dengan semua field kosong → error | ✅ PASS |
| 4 | `test_04_login_invalid_credentials` | Login kredensial tidak valid → error | ✅ PASS |

**Total: 4/4 PASS ✅**

---

### 7.2 Hasil `test_auth.py` (Pengujian Lokal)

**Perintah:** `python test_auth.py`  
**Durasi:** ~58 detik  
**Environment:** Windows, XAMPP Apache, MySQL, ChromeDriver

```
test_TC_LOG_01_valid_credentials ... ok
test_TC_LOG_02_wrong_password ... ok
test_TC_LOG_03_unregistered_username ... ok
test_TC_LOG_04_empty_fields ... ok
test_TC_LOG_05_empty_username_only ... ok
test_TC_LOG_06_redirect_to_register ... ok
test_TC_REG_01_valid_data ... ok
test_TC_REG_02_existing_username ... ok
test_TC_REG_03_password_mismatch ... ok
test_TC_REG_04_empty_fields ... ok
test_TC_REG_05_partial_empty_fields ... ok
test_TC_REG_06_redirect_to_login ... ok

----------------------------------------------------------------------
Ran 12 tests in 58.067s

OK
```

| No | Kode TC | Modul | Skenario | Status |
|---|---|---|---|:---:|
| 1 | TC-LOG-01 | Login | Kredensial valid → redirect sukses | ✅ PASS |
| 2 | TC-LOG-02 | Login | Password salah → tetap di login.php | ✅ PASS |
| 3 | TC-LOG-03 | Login | Username tidak terdaftar → pesan error | ✅ PASS |
| 4 | TC-LOG-04 | Login | Semua field kosong → pesan error | ✅ PASS |
| 5 | TC-LOG-05 | Login | Hanya password diisi → pesan error | ✅ PASS |
| 6 | TC-LOG-06 | Login | Link navigasi ke Register ada | ✅ PASS |
| 7 | TC-REG-01 | Register | Data valid → redirect sukses | ✅ PASS |
| 8 | TC-REG-02 | Register | Nama duplikat → pesan error | ✅ PASS |
| 9 | TC-REG-03 | Register | Password ≠ Re-password → pesan error | ✅ PASS |
| 10 | TC-REG-04 | Register | Semua field kosong → pesan error | ✅ PASS |
| 11 | TC-REG-05 | Register | Sebagian field kosong → pesan error | ✅ PASS |
| 12 | TC-REG-06 | Register | Link navigasi ke Login ada | ✅ PASS |

**Total: 12/12 PASS ✅**

---

### 7.3 Rekapitulasi Keseluruhan

| File Pengujian | Jumlah TC | PASS | FAIL | Durasi |
|---|:---:|:---:|:---:|---|
| `test_app.py` | 4 | 4 | 0 | ~16 detik |
| `test_auth.py` | 12 | 12 | 0 | ~58 detik |
| **TOTAL** | **16** | **16** | **0** | **~74 detik** |

> **Tingkat Keberhasilan: 100% (16/16)**

---

## 8. Temuan (Bug yang Ditemukan)

Selama proses pengujian, ditemukan satu bug logika pada kode PHP:

> [!WARNING]
> **Bug di `register.php` baris 32:**
> Fungsi `cek_nama($name, $con)` dipanggil dengan parameter **`$name`** (nama lengkap pengguna), bukan `$username`. Akibatnya, sistem hanya mengecek duplikasi berdasarkan **nama**, bukan **username** seperti yang seharusnya. Dua pengguna dengan username yang sama dapat mendaftar selama nama mereka berbeda.
>
> **Rekomendasi:** Ubah pemanggilan fungsi menjadi `cek_nama($username, $con)` dan sesuaikan query SQL di dalamnya untuk mengecek kolom `username`, bukan `name`.

---

## 9. Cara Menjalankan Pengujian

### Menjalankan Lokal:
```powershell
# Prasyarat: XAMPP (Apache + MySQL) harus aktif

# 1. Import database (sekali saja)
D:\xampp\mysql\bin\mysql.exe -u root -e "CREATE DATABASE IF NOT EXISTS quiz_pengupil;"
# Lalu import via phpMyAdmin: http://localhost/phpmyadmin

# 2. Jalankan test_app.py
cd D:\quiz-pengupil-main\tests
python test_app.py

# 3. Jalankan test_auth.py
python test_auth.py
```

### Menjalankan via GitHub Actions:
Setiap **push** ke branch `main` akan memicu pipeline CI/CD secara otomatis. Pipeline dapat juga dijalankan manual melalui:
**GitHub → Repository → Actions → Selenium Tests → Run workflow**

---

## 10. Kesimpulan

Pengujian otomatis terhadap modul **Login** dan **Register** aplikasi Quiz Pengupil telah berhasil dilaksanakan menggunakan **Selenium WebDriver** dengan total **16 testcase**, dan seluruhnya **berhasil (PASS)**. 

Penggunaan **Stub** (database MySQL dan server Apache) dan **Driver** (ChromeDriver dan framework `unittest`) terbukti efektif dalam mensimulasikan lingkungan pengujian tanpa perlu interaksi manual dari pengguna. Pipeline **CI/CD GitHub Actions** juga telah berhasil dikonfigurasi untuk menjalankan pengujian secara otomatis pada setiap perubahan kode.

**Repository:** https://github.com/tbimantara04-hub/quiz
