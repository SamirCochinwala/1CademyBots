import sys
import os

from datetime import datetime, date, time
import re
import time
import random
import json
import csv

import requests
from bs4 import SoupStrainer, BeautifulSoup, element

# import unicodedata

from CustomSearchAPIKey import CustomSearchAPIKey, SearchEngineID

from WebsiteScapingLibrary import soupStructure
from WikipediaScrapingLibrary import WikipediaPageStats

from MicrosoftResearchApi import getExpression

def num(stringObj):
    try:
        return int(stringObj)
    except ValueError:
        try:
            return float(stringObj)
        except ValueError:
            return int(stringObj.replace(',', ''))

# Check if the string is in ASCII or not.


def is_ascii(s):
    ASCIICharNum = 0
    for c in s:
        if ord(c) < 191:
            ASCIICharNum += 1
    if len(s) != 0 and ASCIICharNum / len(s) >= 0.99:
        return True
    else:
        return False


# Extract search results from google.
def GoogleSearchAPIResults(searchTerm, numberOfPages):

    searchURL = "https://www.googleapis.com/customsearch/v1/siterestrict?cx=" + \
        SearchEngineID + "&key=" + CustomSearchAPIKey + "&q=" + searchTerm

    # Request a search query from Google and return the respone.
    try:
        response = requests.get(searchURL)
        response = response.text

        response = json.loads(response)
    except:
        print("An existing connection was forcibly closed by Google.")
        response = {}

    while not 'items' in response:
        print("Search URL: " + searchURL)
        print("Cannot find items in the search results. Enter a new search query:")
        searchTerm = input()
        searchURL = "https://www.googleapis.com/customsearch/v1/siterestrict?cx=" + \
            SearchEngineID + "&key=" + CustomSearchAPIKey + "&q=" + searchTerm
        if searchURL == "1":
            return []
        try:
            response = requests.get(searchURL)
            response = response.text

            response = json.loads(response)
        except:
            print("That was a wrong URL.")

    results = []
    for responseItem in response['items']:
        results.append(
            {'title': responseItem['title'], 'hyperlink': responseItem['link']})

    # return the results.
    return results


def IsWikipageAppropriate(title, hyperlink):

    if ("Category:" in title or "User:" in title or "Talk:" in title or "User talk:" in title or
            "Book:" in title):
        return False, None

    wikipediaSoup = soupStructure(hyperlink)
    print("Wikipedia page Soup is Retrieved.")

    trialNum = 0
    while wikipediaSoup == "" and trialNum < 10:
        trialNum += 1
        print("Wikipedia page:" + hyperlink +
              " Soup is not retreived. Please enter an appropriate URL:")
        # hyperlink = input()
        # if hyperlink == "1":
        #     return False, None
        wikipediaSoup = soupStructure(hyperlink)

    if wikipediaSoup != "":
        resultRow = WikipediaPageStats(
            hyperlink, wikipediaSoup, title, 'list')

        trialNum = 0
        while resultRow == [] and trialNum < 10:
            trialNum += 1
            print("wikipageURL:", hyperlink,
                  "is not found. Please enter a new one:")
            # hyperlink = input()
            # if hyperlink == "1":
            #     return False, None
            wikipediaSoup = soupStructure(hyperlink)

            innerTrialNum = 0
            while wikipediaSoup == "" and innerTrialNum < 10:
                innerTrialNum += 1
                print("Wikipedia page:" + hyperlink +
                      " Soup is not retreived. Please enter an appropriate URL:")
                # hyperlink = input()
                # if hyperlink == "1":
                #     return False, None
                wikipediaSoup = soupStructure(hyperlink)

            resultRow = WikipediaPageStats(
                hyperlink, wikipediaSoup, title, 'list')

        if resultRow == []:
            return False, None
        print("Wikipedia page Stats:", resultRow)

        # If the edit protection os the page is not None:
        if resultRow["editProtectionLevel"].lower() != "none":
            print("The Wikipedia page is edit protected. Do not recommend it.")
            return False, None
        if resultRow["qualityClass"].lower() == "stub-class":
            print("The Wikipedia page is a Stub. Do not recommend it.")
            return False, None
        # if resultRow[3].lower() == "b-class":
        #   print "The Wikipedia page is a B-Class. Do not recommend it."
        #   return False, None
        # if resultRow[3].lower() == "b+ class":
        #   print "The Wikipedia page is a B+ class. Do not recommend it."
        #   return False, None
        # if resultRow[3].lower() == "ga-class":
        #   print "The Wikipedia page is a GA-Class. Do not recommend it."
        #   return False, None
        # if resultRow[3].lower() == "a-class":
        #   print "The Wikipedia page is a A-Class. Do not recommend it."
        #   return False, None
        # if resultRow[3].lower() == "fa-class":
        #   print "The Wikipedia page is a FA-Class. Do not recommend it."
        #   return False, None
        if num(resultRow["viewsNum"]) < 1000:
            print(
                "The Wikipedia page has been viewed less than 1000 times. Do not recommend it.")
            return False, None

        print("The Wikipedia page is OK to recommend.")
        return True, resultRow

#Returns a list of html reference tag ids
#
#accepts: bs4 Tag as SummaryContainer
#
def GetReferencesFromSummaryContainer(SummaryContainer):
    found = []
    for child in SummaryContainer.children:
        if isinstance(child, element.Tag):

            #Each article summary ends with this table so we don't want
            #any <p> tags after this
            if child.has_attr('id') and child['id'] == "toc":
                return found

            #Each article container has a blank <p> tag that we want to ignore
            if child.has_attr('class') and "mw-empty-elt" in child['class']:
                continue

            #Our summary paragraph(s)
            if child.name == 'p':
                references = child.find_all('sup')
                for ref in references: 
                    found.extend([tag['href'][1:] for tag in ref.find_all('a')])


    #We should have returned our list already, so if we get this far
    #something is probably wrong with the structure of our soup article
    return []


#Builds a dictionary of systems for 
def BuildArticleStructure(url):
    pass


# datatsetFileName = input(
#     "Enter the name of the dataset csv file without any sufix:")
# while len(datatsetFileName) <= 1:
#     datatsetFileName = input(
#         "Enter the name of the dataset csv file without any sufix:")
datatsetFileName = "COVID_articles"

searchQuery = input("Enter the search query string:")
while len(searchQuery) <= 1:
    searchQuery = input("Enter the search query string:")

#Sometimes google search API will return a blank wikipedia url (http://wikipedia.com)
#This is to remove those results from the list before retreiving every article
GoogleSearchResults = []
for result in GoogleSearchAPIResults(searchQuery, 1):
    if result['title'] != 'Wikipedia':
        GoogleSearchResults.append({'title': result['title'], 'hyperlink': result['hyperlink']}) 

#print(GoogleSearchResults)

with open(datatsetFileName + '.csv', 'w') as fw:
    writer = csv.writer(fw)

    resultRow = ['Wikipage1', 'WikipageURL1', 'Wikipage2', 'WikipageURL2',
                 'Wikipage3', 'WikipageURL3', 'Wikipage4', 'WikipageURL4',
                 'Wikipage5', 'WikipageURL5', 'Wikipage6', 'WikipageURL6',
                 'Wikipage7', 'WikipageURL7', 'Wikipage8', 'WikipageURL8',
                 'Wikipage9', 'WikipageURL9', 'Wikipage10', 'WikipageURL10']
    writer.writerow(resultRow)
    resultRow = []
    with open(datatsetFileName + '_Stats.csv', 'w') as fw:
        writer_Stats = csv.writer(fw)

        wikipageResultRow = ['ID', 'Title', 'Edit Protection Level', 'Class', 'Importance',
                             'Page Length', '# watchers', 'Time of Last Edit',
                             '# redirects to this page', 'Page Creation Date', 'Total # edits',
                             'Total # distinct authors', 'Recent # edits (over the past month)',
                             'Recent # distinct authors', '# views (last 90 days)',
                             'Total # references', '# references published after 2010',
                             '# External Hyperlinks']
        writer_Stats.writerow(wikipageResultRow)

        for searchRIndex in range(len(GoogleSearchResults)):

            recommendedTitle = GoogleSearchResults[searchRIndex]['title']
            recommendedURL = GoogleSearchResults[searchRIndex]['hyperlink']

            flag, wikipageResultRow = IsWikipageAppropriate(
                recommendedTitle, recommendedURL)
            
            #flag is false if the article should not be used
            if not flag:
                continue

            

            #TODO Pass reference data to MicrosoftResearchAPI

            #adds the current wikistats to the next row in the csv, changing bytes to string when necessary
            writer_Stats.writerow(list(str(item) if not str(item).startswith("b'") else item.decode() for item in wikipageResultRow.values()))

            resultRow.extend(
                [recommendedTitle, recommendedURL])

        writer.writerow(resultRow)

if __name__ == '__main__':#TODO remove 
    pass