import WikipediaScrapingLibrary
from bs4 import element
import unittest
import re

#TODO implement caching one article for successive calls to 
#getReferenceData and getPrerequisiteData
#
cache_url = None
cache = None

#Returns a list of summary paragraphs as bs4 tags 
#
#accepts: bs4 object for the article
#
def getSummaryParagraphs(articleSoup):
    found = []

    summary_container = articleSoup.find(id="mw-content-text")
    if summary_container == None:
        return found

    for child in list(summary_container)[0].children:
        
        if isinstance(child, element.Tag):

            #Some articles have a <p> tag that only serves to hold coordinates
            #So we want to skip that one
            if child.find_all(id='coordinates'):
                continue

            #The only common identifier shared by summary paragraphs is that they contain
            #<a> tags
            #So that's what were going with
            if child.name == 'p' and len(list(child.find_all("a"))) > 0:
                found.append(child)


            #There is not a consistent identifier for the TOC so we just get paragraphs
            #until we get to a different tag
            elif len(found) > 0:
                return found
            

    #We should have returned our list already, so if we get this far
    #something is probably wrong with the structure of our soup article
    return []


##
#Returns a list of prerequisite article urls as strings 
#
#
#Accepts url as string
##
def getPrerequisiteDataFromArticle(url):
    print("Getting summary from article: ", url)

    soup = WikipediaScrapingLibrary.soupStructure(url)
    
    prerequisites = []
    
    summary_paragraphs = getSummaryParagraphs(soup)

    for paragraph in summary_paragraphs:
        for link in paragraph.find_all('a'):
            if link.has_attr('href') and '#cite_note' not in link['href']:
                prerequisites.append('https://en.wikipedia.org' + link['href'])
    
    if len(prerequisites) == 0:
        print("Found no prerequisites, flagging article as abnormality: ", url)#TODO implement logging

    return prerequisites

#Returns a list of references listed in the summary of a
#wikipedia article
#
#accepts a url as string
#
def GetReferenceDataFromArticle(url):
    print("Getting summary from article: ", url)#TODO remove
    soup = WikipediaScrapingLibrary.soupStructure(url)

    #The wiki html structure does not explicitly define the summary paragraphs so we
    #have to find the <p> tags which are direct descendents of the <div> below id#mw-content-text
    summary_paragraphs = getSummaryParagraphs(soup)
    
    ExtractedReferences = []
    ref_section = soup.find('ol', {'class':"references"})
    
    if not ref_section:
        print("Trouble finding reference section, flagging")#TODO implement logging
        return []

    found = []

    for paragraph in summary_paragraphs:
        #TODO Do we want to take into account summary references which are marked as 'wiki/Wikipedia:Citation_needed'?
        for link in paragraph.find_all('a', {'href': re.compile(r'#cite_note.+')}):
            ref = ref_section.find(id=link['href'][1:])
            
            try:
                found.append((ref.find('a', {'class': re.compile(r'external')})['href'], ref.find('cite').text))
            except Exception as e:
                print("Error getting citation information from: ", url)#TODO Implement Logging
            
    return found

#This is just to test this module on a variety of wiki articles to ensure that 
#it works in 99% of cases
if __name__ == '__main__':
    print(GetReferenceDataFromArticle('https://en.wikipedia.org/wiki/Ford_Motor_Company'))
    #print(len(getSummaryParagraphs(WikipediaScrapingLibrary.soupStructure('https://en.wikipedia.org/wiki/Ford_Motor_Company'))) == 3)
    #print(len(getSummaryParagraphs(WikipediaScrapingLibrary.soupStructure('https://google.com'))) == 0)