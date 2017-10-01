import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import datetime

#
# Parse the html and return listing information
#
def parse_listing(conn, driver):
    today = datetime.date.today().isoformat()
    cur = conn.cursor()
    # Find all items with listing_info class
    listing_items = driver.find_elements_by_class_name('listing_info')

    # Get Title, Addres, .... from listing info
    # item = driver.find_element_by_class_name('listing_info')
    for item in listing_items:
        h = "prop_info, prop_type, address, agent, list_type, date, psf, size, url, ins_date"
        title = item.find_element_by_class_name('bluelink')
        v = [title.text]
        item_url = title.get_attribute('href')
        try:
            v.append(item.find_element_by_xpath('div/div/div/b').text)
        except:
            v.append("")
        v += (x.text for x in item.find_elements_by_class_name('top3'))

        if len(v) == 7:
            # change listing type, list date, psf and size
            r = re.search("([0-9]*) sqft.*", v[6])
            v.append(int(r.group(1)))
            # v.append(r.group(1))

            r = re.search("S. ([0-9\.]*) psf", v[5])
            v[6] = float(r.group(1))
            # v[6] = r.group(1)

            r = re.search("(.*isted) on (.*)", v[4])
            v[4] = r.group(1)
            v[5] = datetime.datetime.strptime(r.group(2), '%b %d, %Y').strftime('%Y-%m-%d')
            v.append(item_url)
            # listing_info = dict(zip(h,v))
            # print(v)

            vcnt = len(v)
            vals = ""
            for i in range(vcnt):
                if (type(v[i]) == str):
                    v[i] = v[i].replace("'", "")
                    vals += "'"+v[i]+"'"
                else:
                    vals += str(v[i])
                if (i < vcnt - 1):
                    vals += ', '

            # If item is not in database, insert into DB, and update as New Listing
            if v[7] >= 700:
                sql_sel = "SELECT * from listing WHERE prop_info='" + v[0] + "' AND prop_type='" + v[1] + "' AND address='" + v[2] + "' AND agent='" + v[3] + "' AND cast(psf as decimal(6,2))=" + str(v[6]) + " AND size=" + str(v[7])
                cur.execute(sql_sel)
                if cur.rowcount == 0:
                    sql_ins = "INSERT INTO %s (%s) VALUES(%s, '%s')" % ("listing", h, vals, today)
                    cur.execute(sql_ins)
                    print(sql_ins)
                else:
                    # If item is already in database, change to "Re-Listing" and update date as per item
                    sql_upd = "UPDATE ..."
                    # print('Old listing:', v)
    conn.commit()

# Connect to database
conn = pymysql.connect(host='192.168.2.71', port=3306, user='root', passwd='Wze!501813', db='commercialguru', charset='utf8')
cur = conn.cursor()

# Open First page
url = "http://www.commercialguru.com.sg/find-commercial-properties?listing_type=rent&search_type=district&property_type=R&property_type_code%5B%5D=SHOP&property_type_code%5B%5D=FOOD&mrt=&address=&property_id=&distance=0.5&latitude=&longitude=&interest=&hdb_type_group=&minprice=&maxprice=15000&minsize_land=&maxsize_land=&freetext=&minsize=500&maxsize=&minpsf=&maxpsf=&listing_posted=&min_latitude=&max_latitude=&min_longitude=&max_longitude=&submit="
driver = webdriver.Firefox(executable_path=r'D:\Program Files (x86)\Python36-32\Lib\site-packages\selenium\common\geckodriver.exe')
driver.get(url)
try:
    wait = WebDriverWait(driver, 60)
    last_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Last')))
except:
    print("Timed out!")
    driver.quit()


# Get number of pages
nPagesRE = '(?P<url1>.*/find-commercial-properties/property-for-rent/)(?P<pages>[0-9]*?)(?P<url2>.property_type.*)'
r = re.search(nPagesRE,last_link.get_attribute("href") )
parse_listing(conn, driver)

# '''
# Get list of URL to scrape
url_list = []
for x in range(2,int(r.group('pages'))+1):
    url_list.append(r.group('url1') + str(x) + r.group('url2'))

#
# Loope through the list of pages
#
for url in url_list:
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 60)
        last_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Prev')))
    except:
        print("Timed out!")
        driver.quit()
    parse_listing(conn, driver)
# '''

#
# Close the browser
#
driver.quit()
cur.close()
conn.close()
