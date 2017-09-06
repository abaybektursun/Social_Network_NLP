import time
import json
import sys
import Review
from bs4 import BeautifulSoup
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

username = # your email here
password = # your password here

# Manual options for the company, num pages to scrape, and URL
pages = 595 #5
#DXC= 88 pages
#HPE: = 542
#CSC = 595
source = "Glassdoor"

if (sys.argv[1] =='DXC'):
	companyName = "DXC-Technology"
	companyURL = "https://www.glassdoor.com/Reviews/DXC-Technology-Reviews-E1603125.htm"
elif (sys.argv[1] =='HPE'):
	companyName = "Hewlett-Packard-Enterprise"
	companyURL = "https://www.glassdoor.com/Reviews/Hewlett-Packard-Enterprise-HPE-Reviews-E1093046.htm"
elif (sys.argv[1]=='CSC'):
	companyName = "CSC"
	companyURL = "https://www.glassdoor.com/Reviews/CSC-Reviews-E169.htm"
else: 
	companyName = ""
	companyURL = ""


def obj_dict(obj):
    return obj.__dict__
#enddef

def json_export(data):
	jsonFile = open(companyName + "_reviews2.json", "w")
	jsonFile.write(json.dumps(data, indent=4, separators=(',', ': '), default=obj_dict))
	jsonFile.close()
#enddef

def init_driver():
    #driver = webdriver.Chrome(executable_path = "./chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
	#driver = webdriver.Chrome(executable_path=driver_location, chrome_options=options)
    driver = webdriver.Chrome(executable_path = "C:/chromedriver/chromedriver.exe", chrome_options=options)
    driver.wait = WebDriverWait(driver, 10)
    return driver
#enddef

def login(driver, username, password):
    driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
        user_field = driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "username")))
        pw_field = driver.find_element_by_class_name("signin-password")
        login_button = driver.find_element_by_id("signInBtn")
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        time.sleep(1)
        pw_field.send_keys(password)
        time.sleep(1)
        login_button.click()
    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
#enddef

def parse_reviews_HTML(reviews, data, counter):
	reviewid = 10 * counter
	for review in reviews:	
		recommend = "-"
		summary = "-"
		date = review.find("time", { "class" : "date" }).getText().strip()
		#title = review.find("span", { "class" : "summary"}).getText().strip()
		title = review.find("span", { "class" : "summary"}).getText().encode('utf-8').strip()
		#role = review.find("span", { "class" : "authorJobTitle"}).getText().strip()
		role = review.find("span", { "class" : "authorJobTitle"}).getText().encode('utf-8').strip()
		outcomes = review.find_all("div", { "class" : ["tightLt", "col"] })
		if (len(outcomes) > 0):
			recommend = outcomes[0].find("span", { "class" : "middle"}).getText().strip()
		#endif
		if (len(outcomes) > 1):
			summary = outcomes[1].find("span", { "class" : "middle"}).getText().strip()
		#endif
		pros = review.find("p", { "class" : "pros"})
		if (pros):
			s = pros.find("span", { "class" : ["link", "moreLink"] })
			if (s):
				s.extract() # Remove the "Show More" text and link if it exists
			#endif
			#pros = pros.getText().strip()
			pros = pros.getText().encode('utf-8').strip()
		cons = review.find("p", { "class" : "cons"})
		if (cons):
			s = cons.find("span", { "class" : ["link", "moreLink"] })
			if (s):
				s.extract() # Remove the "Show More" text and link if it exists
			#endif
			#cons = cons.getText().strip()
			cons = cons.getText().encode('utf-8').strip()
		#endif
		advicetomgt = review.find("p", { "class" : "adviceMgmt"})
		if (advicetomgt):
			s = advicetomgt.find("span", { "class" : ["link", "moreLink"] })
			if (s):
				s.extract() # Remove the "Show More" text and link if it exists
			#endif
			#advicetomgt = advicetomgt.getText().strip()
			advicetomgt = advicetomgt.getText().encode('utf-8').strip()
		#endif
		r = Review.Review(source, reviewid, date, title, role, recommend, summary, pros, cons, advicetomgt)
		reviewid = reviewid + 1
		data.append(r)
	#endfor
	return data
#enddef

def get_data(driver, URL, startPage, endPage, data, refresh):
	if (startPage > endPage):
		return data
	#endif
	print "\nPage " + str(startPage) + " of " + str(endPage)
	#currentURL = URL + "_IP" + str(startPage) + ".htm"
	if (startPage == 1):
		currentURL = URL + ".htm"
	else:
		currentURL = URL + "_P" + str(startPage) + ".htm"
	#endif
	time.sleep(2)
	#endif
	if (refresh):
		driver.get(currentURL)
		print "Getting " + currentURL
	#endif
	time.sleep(2)
	HTML = driver.page_source
	#soup = BeautifulSoup(HTML, "html.parser")
	soup = BeautifulSoup(HTML, "lxml")
	#reviews = soup.find_all("li", { "class" : ["empReview", "padVert"] })
	reviews = soup.find_all("li", { "class" : [" empReview cf ", "padVert"] })
	if (reviews):
		data = parse_reviews_HTML(reviews, data, startPage)
		print "Page " + str(startPage) + " scraped."
		if (startPage % 10 == 0):
			print "\nTaking a breather for a few seconds ..."
			time.sleep(10)
		#endif
		get_data(driver, URL, startPage + 1, endPage, data, True)
	else:
		print "Waiting ... page still loading or CAPTCHA input required"
		time.sleep(3)
		get_data(driver, URL, startPage, endPage, data, False)
	#endif
	return data
#enddef

if __name__ == "__main__":
	driver = init_driver()
	time.sleep(3)
	print "Logging into Glassdoor account ..."
	login(driver, username, password)
	time.sleep(5)
	print "\nStarting data scraping ..."
	data = get_data(driver, companyURL[:-4], 1, pages, [], True)
	print "\nExporting data to " + companyName + "_reviews.json"
	json_export(data)
	driver.quit()
#endif