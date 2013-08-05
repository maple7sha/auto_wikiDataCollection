import csv
import sys
import cookielib
import urllib
import urllib2
import requests
import mechanize
from bs4 import BeautifulSoup
from sets import Set
import unittest, time, re
import getpass

#http://stockrt.github.io/p/emulating-a-browser-in-python-with-mechanize/
# request for following url for scraping
def get_html(url, usr, pwd):
    br = mechanize.Browser()
    cj = cookielib.CookieJar()
    br.set_cookiejar(cj)
    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)
    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    page = br.open(url)
    br.select_form(name='loginform')
    br.form["os_username"] = usr
    br.form["os_password"] = pwd
    out = br.submit()
    data = out.read()
    return data

def does_not_have_Adapt(s):
    return (s != 'Adaptavist Theme Builder')

# use beautifulsoup to get a list of links
def get_links(data_html):
    soup = BeautifulSoup(data_html)
    tds = soup.findAll('td', {'class':'confluenceTd'})
    links = []
    a_set = Set([])
    for td in tds:
        links += td.findAll('a', href=True, text=does_not_have_Adapt)
    for link in links:
        a_set.add('https://wikis.uit.tufts.edu'+link['href'])
    f  = open('a_set.html', 'w')
    f.write(str(a_set))
    return a_set

def output_csv(a_set):
    out = open('out.csv', 'w')
    for row in a_set:
        out.write('%s' % row)
    out.close()

def get_admin_email_date(a_set, usr, pwd):
    count = 0
    f = open('wiki_info.csv', 'wb')
    writer = csv.writer(f)
    header = ['URL','DATE', 'EMAILS']
    writer.writerow(header)
    for baseurl in a_set:
        count += 1
        id = baseurl[baseurl.find("/display/")+9:]
        print id
        #try:
        br = mechanize.Browser()
        page = br.open("https://wikis.uit.tufts.edu/confluence/spaces/spacepermissions.action?key=" + id)
        br.select_form(name='loginform')
        br.form["os_username"] = usr
        br.form["os_password"] = pwd
        out = br.submit()
        data = out.read()
        elist = _get_admin_email_date(data)
        # get last edited date!
        date = ''
        try:
            date_page = br.open("https://wikis.uit.tufts.edu/confluence/pages/recentlyupdated.action?&url_xsrfToken()&key=" + id)
            date_soup = BeautifulSoup(date_page)
            latest_li = date_soup.find('li', {'class':'first update-item'})
            date = str(latest_li.find('div', {'class':'update-item-date'}).string)
        except:
            date = "DIY"
        elist.insert(0, baseurl)
        elist.insert(1, date)
        headers = ['url', 'date', 'email']
        writer.writerow(elist)
    f.close()

def _get_admin_email_date(data):
    ulist = []
    elist = []
    # first, get all utlns
    soup = BeautifulSoup(data)
    trs = soup.findAll('tr', {'class':'key-holder'})  # but for groups authorities, it does not have class defined!
    # that particular table does not have 'class:key-holder'; have to add it manually
    grp_tb = soup.find('table', {'id':'gPermissionsTable'})
    grp_trs = grp_tb.findAll('tr')
    grp_trs = grp_trs[2:]
    trs = trs + grp_trs
    for tr in trs:
        if tr.findAll('td')[14].find('img')['src'] == "/confluence/s/1925/11/_/images/icons/emoticons/check.gif":
            try:
                ulist.append(tr['data-key'])
            except:
                elist.append(tr.findAll('td')[0].text.strip())

    # then, search for email in utln
    for utln in ulist:
        minibr = mechanize.Browser()
        minibr.set_handle_robots(False)
        page = minibr.open("http://whitepages.tufts.edu")
        minibr.select_form(name='search')
        minibr.form["search"] = str(utln)
        out = minibr.submit()
        minidata = out.read()
        minisoup = BeautifulSoup(minidata)
        try:
            href = str(minisoup.find('a', {'href': re.compile("^mailto:")}).string)
            elist.append(href)
        except:
            elist.append(utln)
    return elist

def main():
    username = ''

    password = ''

    url = 'https://wikis.uit.tufts.edu/confluence/admin/plugins/macrostats/stats.action'
    data_html = get_html(url, username, password)
    a_set = get_links(data_html)
    list = output_csv(a_set)
    get_admin_email_date(a_set, username, password)

if __name__ == '__main__':
    main()



#find href

#    tables = soup.findAll('table', {'id':re.compile("PermissionsTable$")})
#    for table in tables:
#        table.findAll('tr', {'class':'key-holder'})

#    soup = BeautifulSoup(data_html)
#    tds = soup.findAll('td', {'class':'confluenceTd'})
#    links = []
#    a_set = Set([])
#    for td in tds:
#        links += td.findAll('a', href=True, text=does_not_have_Adapt)
#    for link in links:
#        a_set.add('https://wikis.uit.tufts.edu'+link['href'])


# write list of links to csv
# def write_links(list):

#def get_lastEditDate(a_set):
#    print 'haha'
#    driver = webdriver.Firefox()
#    driver.get('https://wikis.uit.tufts.edu/confluence/pages/recentlyupdated.action?atl_token=XvoR-nyY8t&key=medfordit')
#    driver.find_element_by_id("os_username").clear()
#    driver.find_element_by_id("os_username").send_keys(username)
#    driver.find_element_by_id("os_password").clear()
#    driver.find_element_by_id("os_password").send_keys(password)
#    driver.find_element_by_id("loginButton").click()
#    # mountain to be climbed!
#    view = driver.find_element_by_xpath("//div[contains(text(), 'View')]")
#    hover = ActionChains(driver).move_to_element(view)
#    hover.perform()
#    time.sleep(5)
#    for i in range(60):
#        hover2 = ActionChains(driver).move_to_element_with_offset(view, -i*5, 0)
#        hover2.perform()
#        time.sleep(1)


#print out.read().decode("UTF-8")
#page = br.open(url)
#print page.geturl
#output = page.read().decode("UTF-8")
#f  = open('data.txt', 'w')
#f.write(page)



#

#br.add_password(url, username, password)

#r = br.open(url)

#print r.read()













#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

#login_data = urllib.urlencode({'Username': username,

#                               'Password': password})

#opener.open('https://wikis.uit.tufts.edu/confluence/login.action', login_data)

#resp = opener.open(url, login_data) #open the real page



#

#

#f = open('data.txt', 'w')

#f.write(str(resp))

#

#print resp

##req = urllib2.Request(url, login_data)

##response = urllib2.urlopen(req)

##data = response.read()

##print data

#

#

#

## login first before xml can be obtained

#

#

#

##url = 'http://www.someserver.com/cgi-bin/register.cgi'

##values = {'name' : 'Michael Foord',

##          'location' : 'Northampton',

##          'language' : 'Python' }

#

##data = urllib.urlencode(values)

##req = urllib2.Request(url, data)

##response = urllib2.urlopen(req)

##the_page = response.read()

##

##

##

##soup = BeautifulSoup(urllib2.urlopen('https://wikis.uit.tufts.edu/confluence/admin/plugins/macrostats/stats.action').read())

##

##f  = open('data.txt', 'w')

##f.write(str(soup))

#

#

##for row in soup('table', {'class' : 'spad'})[0].tbody('tr'):

##  tds = row('td')

##  print tds[0].string, tds[1].string