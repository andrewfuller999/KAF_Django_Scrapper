import os.path
import glob
from time import sleep
from pyotp import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

login_url = 'https://stage-webpanel.kaf.tradewize.com:20443/login/'
login_email = 'andrew@tradewize.com'
login_pw = 'Add Django Password Here'
downloadDir = '/Users/andrewfuller999/Dropbox/KAF/Django_Downloads/Staging/MBMS'
mbms_url = 'https://stage-webpanel.kaf.tradewize.com:20443/mtrades/mbmstrade/export/?transaction_datetime__gte=2019' \
           '-12-31&transaction_datetime__lte=2019-12-31 '

fp = webdriver.FirefoxProfile()
fp.set_preference('browser.download.folderList', 2)
fp.set_preference('browser.download.manager.showWhenStarting', False)
fp.set_preference('browser.download.dir', downloadDir)
fp.set_preference('browser.helperApps.neverAsk.saveToDisk', "text/csv")

cap = DesiredCapabilities().FIREFOX
cap['marionette'] = False
driver = webdriver.Firefox(capabilities=cap, firefox_profile=fp)


driver.get(login_url)
wait = WebDriverWait(driver, 10)

# enter the email
email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
email.send_keys(login_email)

# enter password
driver.find_element_by_xpath("//input[@name='password']").send_keys(login_pw)

# get the token from google authenticator
totp = TOTP("Add OTP Token Here")
token = totp.now()
print(token)
# enter otp token
driver.find_element_by_xpath("//input[@name='otp_token']").send_keys(token)

# click on the sybmit button to complete 2FA
driver.find_element_by_xpath("//input[@value='Log in']").click()

driver.get(mbms_url)
wait = WebDriverWait(driver, 10)

# click on the sybmit button to complete 2FA
print('Downloading file')
driver.find_element_by_xpath("//select[@name='file_format']/option[text()='csv']").click()
driver.find_element_by_xpath("//input[@value='Submit']").click()

while True:
    if glob.glob("/Users/andrewfuller999/Dropbox/KAF/Django_Downloads/Staging/MBMS/*.csv.part"):
        print('Waiting for file download 1')
        sleep(1)
    elif os.path.isfile('/Users/andrewfuller999/Dropbox/KAF/Django_Downloads/Staging/MBMS/MBMSTrade-2020-01-06.csv'):
        break
    else:
        print('Waiting for file download 2')
        sleep(1)

driver.quit()
