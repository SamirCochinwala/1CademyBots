import re
# import unicodedata

import time

from bs4 import SoupStrainer, BeautifulSoup

from html.parser import HTMLParser

import requests

import urllib
# import urllib2


# Check if the string is in ASCII or not.
# def convert_unicode(s):
#     if isinstance(s, unicode):
#         return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
#     else:
#         return s

def GETRequestFromWebsite(domainName, subDomain, searchTerm, errorCounter, requestCount):

    notRespondedCorrectlyYet = True

    while notRespondedCorrectlyYet:

        # requestCount = requestCount + 1

        # if requestCount % 10 == 0:

        if isinstance(searchTerm, unicode):

            searchTerm = searchTerm.encode('utf-8')

        encoded_Url = urllib.quote_plus(searchTerm)

        try:

            print("Sending request to: " + domainName + subDomain + encoded_Url)

            responseHTML = requests.get(
                domainName + subDomain + encoded_Url, headers=header, timeout=70)

        except:
            errorCounter = errorCounter + 1
            if errorCounter < 10:
                print("\n\nThe website did not return an appropriate response.\n\n")
                continue
            else:

                print("I tried for 10 times, but I am not able to retrieve the content of the page:",
                      domainName + subDomain + encoded_Url)
                return ''

        try:
            soup = BeautifulSoup(responseHTML, 'html5lib')

        except:

            soup = ''

            print("There is a problem with conversion to BeautifulSoup structure.")
        return (responseHTML, soup, errorCounter)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        uniFed = self.fed
        if type(uniFed) == type("string"):
            uniFed = uniFed.decode('utf-8')
        return u' '.join(uniFed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def ifMoreThan10ErrorsDelay4Minutes(errorCounter):

    if errorCounter % 10 == 0:
        print("\n\n\nI encountered more than 10 errors. So I am going to wait for 4 minutes.\n\n\n")
        for minuteCounter in range(4 * errorCounter / 10):
            print(str(4 * errorCounter / 10 - minuteCounter), "minutes left.")
            time.sleep(60)


def domainNameFinder(url):
    return re.search('(?:https?:\/\/)?(?:www.)?([a-zA-Z0-9]+[.][a-zA-Z0-9]+)(?:\/|$|#|[:])', url).group(1)


def soupStructure(url):
    errorCounter = 0
    while True:
        try:
            errorCounter += 1
            print("Sending request to:", url)
            # userAgentObj = UserAgent()
            # user_agent = userAgentGenerator(userAgentObj)
            # header = user_agent
            # html = urllib2.urlopen(url).read()
            response = requests.get(url, verify=False)
            html = response.text
            # html.encoding = 'latin-1'
            soup = BeautifulSoup(html, 'html5lib')
            if soup.title != None or soup.find('div') != None or soup.find('p') != None:
                return soup
            if errorCounter < 10:
                continue
            else:
                print("\n\n\nI am not able to retrieve the soup of the webpage:", url, "\n\nsoup.title:", str(
                    soup.title), "\n\nsoup.find('div'):", str(soup.find('div')), "\n\nsoup.find('p'):", soup.find('p'), "\n\nPlease enter a new url:")

                url = input()
                if url == "1":
                    return ''
        except(e):
            if errorCounter < 10:
                continue

            else:
                print("\n\n\nI am not able to retrieve the content of the webpage:",
                      url, "The error message is:", str(e), "\n\nPlease enter a new url:")
                url = input()
                if url == "-1":
                    return ''


def ifAppropriateSoup(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue):
    soup = soupStructure(url)
    noAppropriateResponse = False
    if soup == '':
        print("Inappropriate Response. There is no soup.")
        noAppropriateResponse = True
    elif soup == None:
        print("Inappropriate Response. There is no soup.")
        soup = False
    elif errorAttribute == '' and errorTag != "" and soup.find(errorTag) != None:
        soup = False
    elif errorAttribute == 'id' and errorTag != "" and soup.find(errorTag, id=errorValue) != None:

        soup = False
    elif errorAttribute == 'class' and errorTag != "" and soup.find(errorTag, class_=errorValue) != None:
        soup = False
    elif errorAttribute == 'idre' and errorTag != "" and soup.find(errorTag, id=re.compile(errorValue)) != None:
        soup = False
    elif errorAttribute == 'classre' and errorTag != "" and soup.find(errorTag, class_=re.compile(errorValue)) != None:
        soup = False
    elif errorAttribute == 'text' and errorTag != "" and soup.find(errorTag, text=re.compile(errorValue)) != None:
        soup = False
    elif criticalAttribute == '' and soup.find(criticalTag) == None:
        print("Inappropriate Response. criticalAttribute:" + criticalAttribute +
              " Soup.find('" + criticalTag + "''):" + str(soup.find(criticalTag)))
        noAppropriateResponse = True
    elif criticalAttribute == 'id' and soup.find(criticalTag, id=criticalValue) == None:
        print("Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" +
              criticalTag + "', id='" + criticalValue + "'):" + str(soup.find(criticalTag, id=criticalValue)))
        noAppropriateResponse = True

    elif criticalAttribute == 'class' and soup.find(criticalTag, class_=criticalValue) == None:
        print("Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag +
              "', class_='" + criticalValue + "'):" + str(soup.find(criticalTag, class_=criticalValue)))
        noAppropriateResponse = True
    elif criticalAttribute == 'idre' and soup.find(criticalTag, id=re.compile(criticalValue)) == None:
        print("Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag +
              "', id=" + "re.compile('" + criticalValue + "')):" + str(soup.find(criticalTag, id=re.compile(criticalValue))))

        noAppropriateResponse = True
    elif criticalAttribute == 'classre' and soup.find(criticalTag, class_=re.compile(criticalValue)) == None:

        print("Inappropriate Response.")
        noAppropriateResponse = True

    return noAppropriateResponse, soup


def scrapeWebsite(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue):

    errorCounter = 0
    noAppropriateResponse, soup = ifAppropriateSoup(
        url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue)
    while noAppropriateResponse == True:
        errorCounter += 1
        if errorCounter % 10 != 0:
            noAppropriateResponse, soup = ifAppropriateSoup(
                url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue)
            continue
        else:
            return False
    return soup
