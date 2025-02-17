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

# URL der Übersichtsseite
overview_url = 'https://tools.fobizz.com/t/school_classes'

# Funktion, um sich einzuloggen
def login(driver, timeout):
    driver.get('https://plattform.fobizz.com/users/sign_in')
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'user_email'))).send_keys(username)
    driver.find_element(By.ID, 'user_password').send_keys(password)
    driver.find_element(By.XPATH, '//input[@value="Einloggen"]').click()

# Hauptfunktion
def main():
    # Chrome-Optionen für den Headless-Modus konfigurieren
    chrome_options = Options()
    try:
        headlessmode = config['webdriver']['headlessmode']
    except KeyError:
        headlessmode = 5

    try:
        timeout = config['webdriver']['timeout']
    except KeyError:
        timeout = 5


    if headlessmode == "True":
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  # Optional, kann helfen, einige Rendering-Probleme zu vermeiden
    chrome_options.add_argument("--window-size=1920x1080")  # Setzt die Fenstergröße, um Ladeprobleme zu vermeiden

    # WebDriver initialisieren
    driver = webdriver.Chrome(options=chrome_options)  # Stellen Sie sicher, dass der ChromeDriver installiert ist
    visited_headlines = []
    updated_headlines = []

    # Übersichtseite besuchen und Links sammeln
    driver.get(overview_url)
    
    # Überprüfen, ob Login erforderlich ist
    if "sign_in" in driver.current_url:
        login(driver, timeout)
        driver.get(overview_url)

    # Links der Klassen sammeln
    class_links = []
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-cy='link-school_class']"))
        )
        class_links = [element.get_attribute('href') for element in elements]
    except:
        print("Keine Links gefunden")

    # Jede Klasse besuchen und Aktionen durchführen
    for url in class_links:
        driver.get(url)

        # Überschriften notieren
        try:
            headlines = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "tools-navbar__itemTitle"))
            )
            for headline in headlines:
                visited_headlines.append(headline.text)
        except:
            print(f"Keine Überschrift auf {url} gefunden")

        # Button "24 Std (bis max. 7 Tage)" prüfen und klicken
        try:
            while True:
                button = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@aria-label='24 Std (bis max. 7 Tage)']"))
                )
                if button.is_displayed():
                    button.click()
                    updated_headlines.append(headline.text)
                else:
                    break
        except Exception as e:
            print(f"Button auf {url} nicht mehr vorhanden oder konnte nicht geklickt werden")


    driver.quit()

    # Erfolgsmeldung
    print("Erfolg! Besuchte Überschriften:")
    for headline in visited_headlines:
        print(headline)

   

if __name__ == "__main__":
    main()