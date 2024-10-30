import csv
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Konfigurationsdatei einlesen
config = configparser.ConfigParser()
config.read('config.ini')

# Benutzername und Passwort aus der Konfigurationsdatei
username = config['login']['username']
password = config['login']['password']

# Pfad zur CSV-Datei
csv_file_path = 'urls.csv'

# Funktion, um sich einzuloggen
def login(driver):
    driver.get('https://plattform.fobizz.com/users/sign_in')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'user_email'))).send_keys(username)
    driver.find_element(By.ID, 'user_password').send_keys(password)
    driver.find_element(By.XPATH, '//input[@value="Einloggen"]').click()

# Hauptfunktion
def main():
    # Chrome-Optionen für den Headless-Modus konfigurieren
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  # Optional, kann helfen, einige Rendering-Probleme zu vermeiden
    chrome_options.add_argument("--window-size=1920x1080")  # Setzt die Fenstergröße, um Ladeprobleme zu vermeiden

    # WebDriver initialisieren
    driver = webdriver.Chrome(options=chrome_options)  # Stellen Sie sicher, dass der ChromeDriver installiert ist
    visited_headlines = []

    with open(csv_file_path, newline='') as csvfile:
        url_reader = csv.reader(csvfile)
        for row in url_reader:
            url = row[0]
            driver.get(url)

            # Überprüfen, ob Login erforderlich ist
            if "sign_in" in driver.current_url:
                login(driver)
                driver.get(url)

            # Überschriften notieren
            try:
                headlines = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "tools-navbar__itemTitle"))
                )
                for headline in headlines:
                    visited_headlines.append(headline.text)
            except:
                print(f"Keine Überschrift auf {url} gefunden")

            # Button "24 Std (bis max. 7 Tage)" prüfen und klicken
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@aria-label='24 Std (bis max. 7 Tage)']"))
                )
                while button.is_displayed():
                    button.click()
            except:
                print(f"Button auf {url} nicht mehr vorhanden oder konnte nicht geklickt werden")

    driver.quit()

    # Erfolgsmeldung
    print("Erfolg! Besuchte und aktualisierte Überschriften:")
    for headline in visited_headlines:
        print(headline)

if __name__ == "__main__":
    main()