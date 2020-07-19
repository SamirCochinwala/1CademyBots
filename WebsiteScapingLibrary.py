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

        # Flag to indicate inapproperiate response.
    notRespondedCorrectlyYet = True

    while notRespondedCorrectlyYet:

        # requestCount = requestCount + 1

        # # if we have not changed our IP address in the last 10 requests:
        # if requestCount % 10 == 0:

        # If the search term is unicode, encript it to string.
        if isinstance(searchTerm, unicode):

            searchTerm = searchTerm.encode('utf-8')

        # Encode the URL into an acceptable URL format.
        encoded_Url = urllib.quote_plus(searchTerm)

        # Try if the website does not return a strange error.
        try:

            print("Sending request to: " + domainName + subDomain + encoded_Url)

            responseHTML = requests.get(
                domainName + subDomain + encoded_Url, headers=header, timeout=70)

        except:
            # If the website did not respond correctly, log the error, pick a new identity and continue to the next round of the loop.

            # Increment the number of error messages.
            errorCounter = errorCounter + 1

            # If there are less than 10 errors:
            if errorCounter < 10:

                # Display the logMessage
                print("\n\nThe website did not return an appropriate response.\n\n")

                # Continue to the loop and search this query again.
                continue

            # Otherwise:
            else:

                print("I tried for 10 times, but I am not able to retrieve the content of the page:",
                      domainName + subDomain + encoded_Url)

                return ''

        try:

            # Convert the html response into BeautifulSoup structure.
            soup = BeautifulSoup(responseHTML, 'html5lib')

        except Exception:

            soup = ''

            print("There is a problem with conversion to BeautifulSoup structure.")

        # Convert the response to the BeautifulSoup format and return the result.
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


# If there are more than 10 errors, delay for 4 minutes.
def ifMoreThan10ErrorsDelay4Minutes(errorCounter):

    if errorCounter % 10 == 0:

        print("\n\n\nI encountered more than 10 errors. So I am going to wait for 4 minutes.\n\n\n")

        # Delays for 240 seconds = 4 minutes.
        for minuteCounter in range(4 * errorCounter / 10):

            print(str(4 * errorCounter / 10 - minuteCounter), "minutes left.")

            time.sleep(60)


def domainNameFinder(url):

    # Find the domain name part of the url.
    return re.search('(?:https?:\/\/)?(?:www.)?([a-zA-Z0-9]+[.][a-zA-Z0-9]+)(?:\/|$|#|[:])', url).group(1)


def soupStructure(url):

    # Number of times the website was not responsive.
    errorCounter = 0

    # While the response has not received correctly, send the request again.
    while True:

        try:

            # Increment errorNumber.
            errorCounter += 1

            print("Sending request to:", url)

            # Define a User Agent object.
            # userAgentObj = UserAgent()

            # Define a random user-agent, and save it as user_agent.
            # user_agent = userAgentGenerator(userAgentObj)
            # header = user_agent

            # Retrive file from the url.
            # html = urllib2.urlopen(url).read()
            response = requests.get(url, verify=False)
            html = response.text

            # Change the response encoding to latin-1.
            # html.encoding = 'latin-1'

            # Convert the html file into the BeautifulSoup structure.
            soup = BeautifulSoup(html, 'html5lib')

            # If there is no problem with the BeautifulSoup structure:
            if soup.title != None or soup.find('div') != None or soup.find('p') != None:

                # Return the soup structure.
                return soup

            # If there are less than 10 errors:
            if errorCounter < 10:
                continue

            # Otherwise:
            else:

                print("\n\n\nI am not able to retrieve the soup of the webpage:", url, "\n\nsoup.title:", str(
                    soup.title), "\n\nsoup.find('div'):", str(soup.find('div')), "\n\nsoup.find('p'):", soup.find('p'), "\n\nPlease enter a new url:")

                url = input()

                if url == "1":
                    return ''
        # If an error raised, send the request again.
        except Exception as e:

            # If there are less than 10 errors:
            if errorCounter < 10:

                continue

            # Otherwise:
            else:

                print("\n\n\nI am not able to retrieve the content of the webpage:",
                      url, "The error message is:", str(e), "\n\nPlease enter a new url:")

                url = input()

                if url == "-1":
                    return ''


def ifAppropriateSoup(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue):

    # Retrieve the BeautifulSoup structure of the webpage.
    soup = soupStructure(url)

    # Define the condition as soup is not available, or criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format.
    noAppropriateResponse = False

    # If there is no soup structure:
    if soup == '':

        print("Inappropriate Response. There is no soup.")

        noAppropriateResponse = True

    # Otherwise, if there is no body tag:ifAppropriateSoup
    elif soup == None:

        print("Inappropriate Response. There is no soup.")

        soup = False

    # Otherwise, if errorAttribute equals '':
    elif errorAttribute == '' and errorTag != "" and soup.find(errorTag) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'id', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'id' and errorTag != "" and soup.find(errorTag, id=errorValue) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'class', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'class' and errorTag != "" and soup.find(errorTag, class_=errorValue) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'idre', and errorTag having errorValue within the critical attribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'idre' and errorTag != "" and soup.find(errorTag, id=re.compile(errorValue)) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'classre', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'classre' and errorTag != "" and soup.find(errorTag, class_=re.compile(errorValue)) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'text', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'text' and errorTag != "" and soup.find(errorTag, text=re.compile(errorValue)) != None:

        soup = False

    # Otherwise, if criticalAttribute equals '':
    elif criticalAttribute == '' and soup.find(criticalTag) == None:

        print("Inappropriate Response. criticalAttribute:" + criticalAttribute +
              " Soup.find('" + criticalTag + "''):" + str(soup.find(criticalTag)))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'id', and criticalTag having criticalValue within the criticalAttribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'id' and soup.find(criticalTag, id=criticalValue) == None:

        print("Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" +
              criticalTag + "', id='" + criticalValue + "'):" + str(soup.find(criticalTag, id=criticalValue)))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'class', and criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'class' and soup.find(criticalTag, class_=criticalValue) == None:

        print("Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag +
              "', class_='" + criticalValue + "'):" + str(soup.find(criticalTag, class_=criticalValue)))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'idre', and criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'idre' and soup.find(criticalTag, id=re.compile(criticalValue)) == None:

        print("Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag +
              "', id=" + "re.compile('" + criticalValue + "')):" + str(soup.find(criticalTag, id=re.compile(criticalValue))))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'classre', and criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'classre' and soup.find(criticalTag, class_=re.compile(criticalValue)) == None:

        print("Inappropriate Response.")
        noAppropriateResponse = True

    return noAppropriateResponse, soup

# Define a function to try a fair number of times to extract the soupStructure of the website.


def scrapeWebsite(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue):

    # Number of times the website has not responded an appropriate soup structure.
    errorCounter = 0

    # Define a function to extract the BeautifulSoup structure and check if the response soup is in a good shape:
    noAppropriateResponse, soup = ifAppropriateSoup(
        url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue)

    # While noAppropriateResponse equals True:
    while noAppropriateResponse == True:

        # Increment the number of times the website has not responded an appropriate soup structure.
        errorCounter += 1

        # If there are less than 10 errors:
        if errorCounter % 10 != 0:

            # Define a function to extract the BeautifulSoup structure and check if the response soup is in a good shape:
            noAppropriateResponse, soup = ifAppropriateSoup(
                url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue)

            continue

        # Otherwise:
        else:

            return False

    return soup
