from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from dateutil import parser
import time
import os
import re
import mail
import config
import datetime as dt

def findButton(driver,buttonText):
    for button in driver.find_elements_by_tag_name("button"):
        if buttonText == button.text:
            return button

def findCenter(driver,class_name,name):
    for elem in driver.find_elements_by_class_name(class_name):
        if re.search(name,elem.text,re.IGNORECASE):
            return elem
    return False

if os.path.isfile("lock"):
   exit("Found a lock file")

# Grace period
first_date = dt.datetime.now() + dt.timedelta(days=config.first_date_buffer)

# last date
last_date = dt.datetime.now() + dt.timedelta(days=10)

os.environ["PATH"] = str(os.environ.get("PATH") + ":" + os.path.curdir )

# HEADLESS CONSOLE MODE
op = webdriver.ChromeOptions()

op.add_argument("--no-sandbox")
op.add_argument("--remote-debugging-port=9222")
op.headless = True

driver = webdriver.Chrome(options=op)
driver.get(config.url)
driver.find_element_by_class_name("cta_button").click()
# Opens a new window lets change the focus
windows = driver.window_handles
driver._switch_to.window(windows[1])
driver.find_elements_by_tag_name("button")[0].click()
time.sleep(1)

driver.find_element_by_id("mat-input-0").send_keys(config.driver_name)
time.sleep(1)
driver.find_element_by_id("mat-input-1").send_keys(config.driver_license)
time.sleep(1)
driver.find_element_by_id("mat-input-2").send_keys(config.driver_password)
time.sleep(1)
driver.find_element_by_class_name("mat-checkbox-inner-container").click()
# SignIN Button
driver.find_elements_by_tag_name("button")[1].click()
print("Signed in as {0}".format(config.driver_name))
time.sleep(3)

examDetail = driver.find_element_by_class_name('appointment-time').text.split('\n')
examDate = parser.parse("{0} {1}".format(examDetail[0],examDetail[1]))
examBuffer = examDate + dt.timedelta(days=+10)

if examDate < last_date :
   fh = open("lock","a")
   fh.write("No more bot play, locking attempts @ {0}.".format(dt.datetime.now()))
   fh.close()
   exit()

# reschudle
time.sleep(4)
findButton(driver,"Reschedule appointment").click()
time.sleep(1)
# Confirm reschudle
findButton(driver,"Yes").click()
print("Reschudling")
time.sleep(1)
# Enter fails here

while findButton(driver,'Search').get_property('disabled'):
    driver.find_element_by_id("mat-input-3").clear()
    time.sleep(1)
    driver.find_element_by_id("mat-input-3").send_keys(config.location)
    driver.find_element_by_id("mat-input-3").send_keys(' ')

    time.sleep(1)
    driver.find_element_by_id("mat-input-3").send_keys(Keys.DOWN)
    driver.find_element_by_id("mat-input-3").send_keys(Keys.RETURN)
    # driver.find_element_by_id("mat-option-34").click()

findButton(driver,'Search').click()
# got the results
for i in config.test_location:
    time.sleep(2)
    print("Looking for centers")
    center = findCenter(driver,"department-container",i)
    if center:
        center.click()
        time.sleep(4)
        print("Got {0} possible option/s.".format(len(driver.find_elements_by_class_name('date-title'))))
        if len(driver.find_elements_by_class_name('date-title')):
            dates = driver.find_element_by_class_name('appointment-listings').get_attribute("innerHTML")
            matched = re.findall("date-title\"\>.*?([A-Z].*?,.*?,.[0-9]{4}).*?<\/div|(mat-button-toggle-[0-9]{1,}-button).*?([0-9]{1,}:[0-9]{1,} (?:am|pm)).*?button\>",dates,re.MULTILINE|re.DOTALL|re.IGNORECASE)
            avTime = parser.parse("{0} {1}".format(matched[0][0],matched[1][2]))
            print("avTime: {0} examDate:{1}".format(avTime,examDate))
            if avTime > first_date and avTime < examDate:
                driver.find_element_by_id(matched[1][1]).click()
                time.sleep(2)
                driver.find_elements_by_tag_name("button")[-1].click()
                time.sleep(2)
                driver.find_elements_by_tag_name("button")[-1].click()
                time.sleep(2)
                # verification page
                driver.find_elements_by_tag_name("button")[-1].click()
                time.sleep(2)
                PIN = mail.checkGmail()
                driver.find_elements_by_class_name('mat-input-element')[-1].send_keys(PIN)
                time.sleep(2)
                driver.find_elements_by_tag_name("button")[-1].click()
            else:
                print("{0} No appointments at {1}".format(dt.datetime.now(),i))
                findButton(driver,'Back').click()

#Logout
findButton(driver,'Sign Out')
print("Logged out")
driver.close()
driver.quit()
