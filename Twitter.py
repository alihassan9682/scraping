import pandas as pd
import time
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


keywords = [
    "Remote work", "Remote working",
    "Hybrid work", "Hybrid working",
    "Onsite work", "Onsite working",
    "On-site work", "On-site working",
    "Work in-person", "Working in-person",
    "Telework", "remote",
    "Return to work", "Return-to-work",
    "Return to office", "Return-to-office",
    "Work from home", "Working from home",
    "Mobile work", "Mobile working",
    "Telecommute",
    "On the road", "On-the-road",
    "Telework",
]

pattern = "|".join(re.escape(keyword) for keyword in keywords)
regex = re.compile(f"({pattern})", re.IGNORECASE)


def configure_webdriver(open_browser=False, stop_loading_images_and_css=False):
    options = webdriver.ChromeOptions()
    if not open_browser:
        options.add_argument("--headless=new")

    prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2,
                                                        'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                        'notifications': 2, 'auto_select_certificate': 2,
                                                        'fullscreen': 2,
                                                        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                        'media_stream_mic': 2, 'media_stream_camera': 2,
                                                        'protocol_handlers': 2,
                                                        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                        'metro_switch_to_desktop': 2,
                                                        'protected_media_identifier': 2, 'app_banner': 2,
                                                        'site_engagement': 2,
                                                        'durable_storage': 2}}

    if stop_loading_images_and_css:
        options.add_argument('--disable-features=EnableNetworkService')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_experimental_option('prefs', prefs)

    options.add_argument("window-size=1200,1100")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36")

    # options.add_extension(extension_path)

    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=options)

    if stop_loading_images_and_css:
        # Enable Chrome DevTools Protocol
        driver.execute_cdp_cmd("Page.enable", {})
        driver.execute_cdp_cmd("Network.enable", {})

        # Set blocked URL patterns to disable images and stylesheets
        blocked_patterns = ["*.jpg", "*.jpeg",
                            "*.png", "*.gif", "*.css", "*.js"]
        driver.execute_cdp_cmd("Network.setBlockedURLs", {
                               "urls": blocked_patterns})
    return driver


def login(driver, email, password):
    time.sleep(5)
    try:
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
    except Exception as e:
        print(e)
        return False

    try:
        driver.find_element(By.TAG_NAME, "input").click()
        driver.find_element(By.TAG_NAME, "input").clear()
        driver.find_element(By.TAG_NAME, "input").send_keys(email)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "r-1awozwy"))
        )
        driver.find_elements(By.CLASS_NAME, "r-1awozwy")[7].click()
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
            )[1].send_keys(password)
        except Exception as e:
            print(e)
            return False
        driver.find_element(
            By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]').click()
        time.sleep(5)
        return True
    except Exception as e:
        print('error', e)
        return False


def contains_keywords(text):
    return regex.search(text)


def load_all_Tweets(driver):
    try:
        Tweets = []
        previous_Articles = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located(
                (By.TAG_NAME, 'article'))
        )
        pre_len = driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            for tweet in previous_Articles:
                try:
                    tweet_des = tweet.find_element(
                        By.CSS_SELECTOR, '[data-testid="tweetText"]').text
                    if contains_keywords(tweet_des):
                        tweet_post = tweet.find_element(
                            By.CSS_SELECTOR, '[data-testid="User-Name"]').text
                        tweet_link = tweet.find_elements(
                            By.XPATH, './/a[@role="link"]')
                        tweet_link = tweet_link[3].get_attribute('href')
                        Tweets.append([tweet_post, tweet_des, tweet_link])
                except:
                    pass
            time.sleep(15)
            driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(15)
            new_len = driver.execute_script(
                "return document.body.scrollHeight")
            new_Articles = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.TAG_NAME, 'article'))
            )
            if pre_len == new_len:
                break
            else:
                previous_Articles = new_Articles
                pre_len = new_len
                print(pre_len)

    except Exception:
        print(Exception)
        import pdb
        pdb.set_trace()

    return Tweets


def request_url(driver, url):
    driver.get(url)


def scrapTweet(driver,filename ):
    tweets = load_all_Tweets(driver)
    scrapped_data = {
        "Display_name": [],
        "User_name": [],
        "Tweet_date": [],
        "Tweet": [],
        "Url": [],
        "Comments": [],
    }
    print('Tweets', len(tweets))
    for tweet in tweets:
        Comments = []
        try:
            tweet_detail = tweet[0].splitlines()
            Display_name = tweet_detail[0]
            User_name = tweet_detail[1]
            Tweet_date = tweet_detail[3]
            driver.get(tweet[2])
            time.sleep(5)
            try:
                comments = driver.find_elements(
                    By.CSS_SELECTOR, '[data-testid="cellInnerDiv"]')

                for comment in comments:
                    try:
                        c = comment.find_element(
                            By.CSS_SELECTOR, '[data-testid="tweetText"]').text
                        Comments.append(c)
                    except:
                        pass
            except:
                print("Tweet might be a link or video")

        except:
            print('tweet not loaded !!!')
        scrapped_data['Display_name'].append(Display_name)
        scrapped_data['User_name'].append(User_name)
        scrapped_data['Tweet_date'].append(Tweet_date)
        scrapped_data['Tweet'].append(tweet[1])
        scrapped_data['Url'].append(tweet[2])
        scrapped_data['Comments'].append(Comments)

    df = pd.DataFrame(scrapped_data)
    df.to_excel(filename, index=False)


# code starts from here
def Twitter(link, job_type):
    print("Twitter")
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        try:
            request_url(driver, link)
            loggedIn = login(driver, '@Ali846424630602', 'laptop969696')
            if loggedIn:
                print("Logged In successfully")
                driver.find_element(By.CSS_SELECTOR, '[role="combobox"]').send_keys(
                    'Remote until:2023-02-01 since:2023-01-01')
                driver.find_element(
                    By.CSS_SELECTOR, '[role="combobox"]').send_keys(Keys.ENTER)
                scrapTweet(driver, 'Twitter.xlsx')
            print('SCRAPING_ENDED')

        except Exception as e:
            print('LINK_ISSUE')

        driver.quit()
    except Exception as e:
        print(e)


Twitter('https://twitter.com/i/flow/login', '')
