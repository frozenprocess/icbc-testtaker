from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dateutil import parser as dateparser
import time
import os
import re
import mail
import config
import datetime as dt
import argparse

def findButton(driver,buttonText):
    for button in driver.find_elements(By.TAG_NAME,"button"):
        if buttonText == button.text:
            return button

def findCenter(driver,class_name,name):
    for elem in driver.find_elements(By.CLASS_NAME,class_name):
        if re.search(name,elem.text,re.IGNORECASE):
            return elem
    return False

# Grace period
first_date = dt.datetime.now() + dt.timedelta(days=config.first_date_buffer)

# last date
last_date = dt.datetime.now() + dt.timedelta(days=10)

os.environ["PATH"] = str(os.environ.get("PATH") + os.path.curdir )

def done():
    driver.close()
    driver.quit()
argparser = argparse.ArgumentParser()
argparser.add_argument("--headless")
args = argparser.parse_args()

options = Options()
# HEADLESS CONSOLE MODE
if args.headless is not None :
    options.add_argument("--headless")

service = Service("./chromedriver")
driver = webdriver.Chrome(options=options,service=service)
driver.get(config.url)

driver.find_element(By.CLASS_NAME,"cta_button").click()
# Opens a new window lets change the focus
windows = driver.window_handles
driver._switch_to.window(windows[1])
driver.find_elements(By.TAG_NAME,"button")[0].click()
time.sleep(1)

driver.find_element(By.ID,"mat-input-0").send_keys(config.driver_name)
time.sleep(1)
driver.find_element(By.ID,"mat-input-1").send_keys(config.driver_license)
time.sleep(1)
driver.find_element(By.ID,"mat-input-2").send_keys(config.driver_password)
time.sleep(1)
driver.find_element(By.CLASS_NAME,"mat-checkbox-inner-container").click()
# SignIN Button
driver.find_elements(By.TAG_NAME,"button")[1].click()
print("Signed in as {0}".format(config.driver_name))
time.sleep(3)

examDetail = driver.find_element(By.CLASS_NAME,'appointment-time').text.split('\n')
examDate = dateparser.parse("{0} {1}".format(examDetail[0],examDetail[1]))

examBuffer = examDate + dt.timedelta(days=+10)

if examDate < last_date :
   fh = open("lock","a")
   fh.write("No more bot play, locking attempts @ {0}.".format(dt.datetime.now()))
   fh.close()
   exit()

# reschedule
time.sleep(4)
findButton(driver,"Reschedule appointment").click()
time.sleep(1)
# Confirm reschedule
findButton(driver,"Yes").click()
print("Reschudling")
time.sleep(1)
# Enter fails here

while findButton(driver,'Search').get_property('disabled'):
    driver.find_element(By.ID,"mat-input-3").clear()
    time.sleep(1)
    driver.find_element(By.ID,"mat-input-3").send_keys(config.location)
    time.sleep(2)
    driver.find_element(By.ID,"mat-input-3").send_keys(' ')

    time.sleep(3)
    driver.find_element(By.ID,"mat-input-3").send_keys(Keys.DOWN)
    driver.find_element(By.ID,"mat-input-3").send_keys(Keys.RETURN)
    # driver.find_element(By.ID,"mat-option-34").click()

findButton(driver,'Search').click()
# got the results
for i in config.test_location:
    time.sleep(2)
    print("Looking for centers")
    center = findCenter(driver,"department-container",i)
    if center:
        center.click()
        time.sleep(4)
        print("Got {0} possible option/s.".format(len(driver.find_elements(By.CLASS_NAME,'date-title'))))
        if len(driver.find_elements(By.CLASS_NAME,'date-title')):
            dates = driver.find_element(By.CLASS_NAME,'appointment-listings').get_attribute("innerHTML")
            matched = re.findall("date-title\"\>.*?([A-Z].*?,.*?,.[0-9]{4}).*?<\/div|(mat-button-toggle-[0-9]{1,}-button).*?([0-9]{1,}:[0-9]{1,} (?:am|pm)).*?button\>",dates,re.MULTILINE|re.DOTALL|re.IGNORECASE)
            avTime = dateparser.parse("{0} {1}".format(matched[0][0],matched[1][2]))
            print("avTime: {0} examDate:{1}".format(avTime,examDate))
            if avTime > first_date and avTime < examDate:
                driver.find_element(By.ID,matched[1][1]).click()
                time.sleep(2)
                findButton(driver,'Review Appointment').click()
                time.sleep(2)
                findButton(driver,'Next').click()
                time.sleep(2)
                # verification page
                findButton(driver,'Send').click()
                time.sleep(2)
                PIN = mail.checkGmail()
                driver.find_elements(By.CLASS_NAME,'mat-input-element')[-1].send_keys(PIN)
                time.sleep(2)
                findButton(driver,'Submit code and book appointment').click()
            else:
                print("{0} No appointments at {1}".format(dt.datetime.now(),i))
                findButton(driver,'Cancel').click()

#Logout
findButton(driver,'Sign Out').click()
print("Logged out")
driver.close()
driver.quit()
