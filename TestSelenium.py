###############################################################################
# File: TestSelenium.py                                                       #
# Author: Andrew Fuller                                                       #
# Description: Python script for scraping MBMS data from KAF Django panel     #
# using Selenium.                                                             #
###############################################################################

__author__ = 'andrewfuller999'

#######################
# Import used modules #
#######################
import os.path
import glob
from time import sleep
from pyotp import *
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#############################
# Set desired configuration #
#############################
# TODO: Ideally this should get set using a Command Line Interface (CLI)
configuration = 'staging'

##########################
# Read the configuration #
##########################
config = ConfigParser()
config.read('config.ini')

#############################################
# Set variables from the configuration file #
#############################################
login_url = config[configuration]['login_url']
login_email = config[configuration]['login_email']
login_pw = config[configuration]['login_pw']
login_otp_token = config[configuration]['login_otp_token']
downloadDir = config[configuration]['downloadDir']
django_export_data_url = config[configuration]['django_export_data_url']

##########################
# Set up Firefox profile #
##########################
fp = webdriver.FirefoxProfile()
fp.set_preference('browser.download.folderList', 2)
fp.set_preference('browser.download.manager.showWhenStarting', False)
fp.set_preference('browser.download.dir', downloadDir)
fp.set_preference('browser.helperApps.neverAsk.saveToDisk', "text/csv")

###############################
# Set up Firefox capabilities #
###############################
cap = DesiredCapabilities().FIREFOX
cap['marionette'] = False

#########################################################################
# Initialize Selenium web driver with required profile and capabilities #
#########################################################################
driver = webdriver.Firefox(capabilities=cap, firefox_profile=fp)

#########################
# Login to Django panel #
#########################
driver.get(login_url)
wait = WebDriverWait(driver, 10)

# enter the login email
email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
email.send_keys(login_email)

# enter the login password
driver.find_element_by_xpath("//input[@name='password']").send_keys(login_pw)

# get the token from google authenticator
totp = TOTP(login_otp_token)
token = totp.now()

# enter the otp token
driver.find_element_by_xpath("//input[@name='otp_token']").send_keys(token)

# click on the submit button to complete 2FA
driver.find_element_by_xpath("//input[@value='Log in']").click()

#######################################################################
# Navigate to the require data export page and initiate data download #
#######################################################################
driver.get(django_export_data_url)
wait = WebDriverWait(driver, 10)

# Select the required export file format to be CSV
driver.find_element_by_xpath("//select[@name='file_format']/option[text()='csv']").click()

# Click on the submit button to initiate data download
print('Downloading file')
driver.find_element_by_xpath("//input[@value='Submit']").click()

#######################################
# Wait for the file to fully download #
#######################################
while True:
    if glob.glob("/Users/andrewfuller999/Dropbox/KAF/Django_Downloads/Staging/MBMS/*.csv.part"):
        print('Waiting for file download 1')
        sleep(1)
    elif os.path.isfile('/Users/andrewfuller999/Dropbox/KAF/Django_Downloads/Staging/MBMS/MBMSTrade-2020-01-06.csv'):
        break
    else:
        print('Waiting for file download 2')
        sleep(1)

####################
# Quit the browser #
####################
driver.quit()
