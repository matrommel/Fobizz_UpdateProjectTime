import configparser
import time
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
        headlessmode = "False"

    try:
        timeout = int(config['webdriver']['timeout'])
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
    failed_urls = []

    # Übersichtseite besuchen und Links sammeln
    driver.get(overview_url)
    
    # Überprüfen, ob Login erforderlich ist
    if "sign_in" in driver.current_url:
        login(driver, timeout)
        driver.get(overview_url)

    # Links der Klassen sammeln
    class_links = []

    # CSS-Selektoren versuchen
    selectors_to_try = [
        "a[href*='school_classes']",           # Links die school_classes enthalten
        ".card a",                             # Links in Karten
        "a[class*='card']",                    # Links mit card in der CSS-Klasse
        "a[href*='/t/']",                      # Alle Tool-Links
    ]

    print("Suche nach Klassen-Links...")

    for i, selector in enumerate(selectors_to_try):
        try:
            print(f"Versuche Selektor {i+1}: {selector}")
            elements = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            potential_links = [element.get_attribute('href') for element in elements if element.get_attribute('href')]

            # Filtere nur Links die zu Klassen führen
            class_links = [link for link in potential_links if link and 'school_classes' in link]

            # Duplikate entfernen
            class_links = list(set(class_links))

            print(f"Gefunden: {len(potential_links)} Links, davon {len(class_links)} eindeutige Klassen-Links")

            if class_links:
                print(f"✓ Erfolg mit Selektor: {selector}")
                break

        except Exception as e:
            print(f"✗ Selektor {selector} fehlgeschlagen: {str(e)}")
            continue

    # Falls immer noch keine Links gefunden
    if not class_links:
        print("Fallback: Alle Links auf der Seite untersuchen...")
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            all_hrefs = [link.get_attribute('href') for link in all_links if link.get_attribute('href')]
            class_links = [link for link in all_hrefs if 'school_classes' in link]
            # Duplikate entfernen
            class_links = list(set(class_links))
            print(f"Fallback gefunden: {len(class_links)} eindeutige Klassen-Links")
        except Exception as e:
            print(f"Auch Fallback fehlgeschlagen: {str(e)}")

    if not class_links:
        print("FEHLER: Keine Klassen-Links gefunden!")

    # Jede Klasse besuchen und Aktionen durchführen
    print(f"Aktualisiere {len(class_links)} Klassen:")

    for i, url in enumerate(class_links):
        print(f"\n--- Klasse {i+1}/{len(class_links)} ---")
        print(f"Besuche: {url}")

        try:
            driver.get(url)

            # Kurz warten bis die Seite geladen ist
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

        except Exception as e:
            print(f"✗ Fehler beim Laden der Seite: {str(e)}")
            failed_urls.append(url)
            continue

        # Überschriften notieren
        current_headline = "Unbekannte Klasse"
        try:
            headlines = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "tools-navbar__itemTitle"))
            )
            if headlines:
                current_headline = headlines[0].text
                visited_headlines.append(current_headline)
                print(f"✓ Gefunden: {current_headline}")
            else:
                print("✗ Keine Überschrift gefunden")
        except Exception as e:
            print(f"✗ Fehler beim Finden der Überschrift: {str(e)}")

        # Button "24 Std (bis max. 7 Tage)" prüfen und klicken
        buttons_clicked = 0
        try:
            while True:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='24 Std (bis max. 7 Tage)']"))
                )

                if button.is_displayed() and button.is_enabled():
                    button.click()
                    buttons_clicked += 1
                    print(f"✓ Button geklickt ({buttons_clicked}x)")

                    # Kurz warten nach dem Klick
                    time.sleep(1)

                    # Schauen ob noch mehr Buttons da sind
                    try:
                        remaining_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='24 Std (bis max. 7 Tage)']")
                        if not remaining_buttons:
                            break
                    except:
                        # Keine weiteren Buttons gefunden
                        break
                else:
                    break

        except Exception as e:
            if buttons_clicked == 0:
                print("✓ Keine Buttons zu aktualisieren (bereits aktuell)")
            else:
                print(f"✗ Fehler beim Button klicken: {str(e)}")

        if buttons_clicked > 0:
            updated_headlines.append(current_headline)
            print(f"✓ {current_headline} aktualisiert ({buttons_clicked} Buttons)")

        if buttons_clicked == 0:
            failed_urls.append(url)
           
    driver.quit()

    # Erfolgsmeldung falls etwas aktualisiert wurde
    if updated_headlines:
        # Duplikate entfernen, indem ein Set verwendet wird
        unique_headlines = list(set(updated_headlines))
        print("Erfolg! Besuchte Klassen:")
        for headline in unique_headlines:
            print(headline)
    else:
        print("Alle Klassen sind aktualisiert")

if __name__ == "__main__":
    main()