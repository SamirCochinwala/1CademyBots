# -*- coding: utf-8 -*-

import re
import csv
import datetime
import time
# import unicodedata

from bs4 import SoupStrainer, BeautifulSoup

from WebsiteScapingLibrary import scrapeWebsite, strip_tags, soupStructure

import requests

from urllib.parse import urlparse, urljoin, quote, unquote, urlunsplit


def num(stringObj):
    try:
        return int(stringObj)
    except ValueError:
        try:
            return float(stringObj)
        except ValueError:
            return int(stringObj.replace(',', ''))


def submitAndPrint(statsFile, title, printableString):
    print(title + printableString, '\n')

    statsContext = "<td>" + printableString + "</td>"
    statsFile.write(statsContext)

# Check if the string is in ASCII or not.
# def convert_unicode(s):
#     if isinstance(s, unicode):
#         return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
#     else:
#         return s


# Send request to Wikipedia by the use of Wikipedia API , and return the response as a Dictionary.
def GETRequestFromWikipedia(request):

    request['action'] = 'query'
    request['format'] = 'json'
    lastContinue = {'continue': ''}

    result = {}
    while True:

        if not 'error' in result:
            req = request.copy()
            req.update(lastContinue)
            responseNotReceived = True
            errorCount = 0

            while responseNotReceived:
                try:
                    response = requests.get(
                        "http://en.wikipedia.org/w/api.php?", params=req)
                    print("Response received from MediaWiki API.")
                    print(response.url)

                    # response.encoding = 'utf-8'
                    result = response.json()
                    responseNotReceived = False

                except:
                    errorCount += 1
                    if errorCount < 10:
                        continue
                    else:
                        result = {'query': []}
                        break

        if 'error' in result:
            print("The Error Message from Wikipedia is:", result['error'])
            time.sleep(10)
            # result = {'query':[ ]}

        else:
            if 'warnings' in result:
                print(result['warnings'])

            if 'query' in result:
                yield result['query']

            if 'continue' not in result:
                print("There is no more data to continue request it from Wikimedia.")
                return

            lastContinue = result['continue']
            print(
                "I am going to continue requesting the rest of the data from Wikimedia.")


def classFinder(url, articleEncodedTitle, desiredCategory):

    qualityClass = "No-Class"
    importanceClass = "No-Class"
    desiredCategoryFound = False

    print("Finding class for url: " + url)
    if "Category:" in url or "User:" in url or "Talk:" in url or "User_talk:" in url or "Book:" in url:
        return "No-Class", "No-Class", False

    talkPageHyperlink = 'http://en.wikipedia.org/wiki/Talk:' + articleEncodedTitle

    # Convert the hyperlink to absolute if it is relative.
    # talkPageHyperlink = urljoin(url, talkPageHyperlink)

    talkSoup = soupStructure(talkPageHyperlink)
    # talkSoup = scrapeWebsite(talkPageHyperlink, 'div', 'id', "catlinks", "b", "text", "Wikipedia does not have a")

    errorCounter = 0
    while (talkSoup == '' or (talkSoup.find('div', id="catlinks") == None and talkSoup.find('b', text="Wikipedia does not have a") == None)) and errorCounter <= 10:

            # print("talkPageHyperlink:", talkPageHyperlink, "is not found. Please enter a new one:")
            # talkPageHyperlink = input()
        talkSoup = soupStructure(talkPageHyperlink)

        errorCounter += 1

    while True:
        ######################################
        # We have to implement error counting.
        ######################################
        try:
            r = requests.get(
                'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles=' + articleEncodedTitle)
            r = r.json()
            query = r['query']
            pages = query['pages']
            break
        except:
            print(
                "\n\n\nI cannot retrieve the revision ID of this article! Error Message: " + str(e))
            time.sleep(1)
    try:
        revisions = list(pages.values())[0]['revisions']
        revisionID = revisions[0]['revid']
    except:
        return "No-Class", "No-Class", False
    # qualityDict = None
    # while True:
        ######################################
        # We have to implement error counting.
        ######################################
        #     try:
        #         r = requests.get(
        #             'https://ores.wmflabs.org/scores/enwiki/wp10/' + str(revisionID))
        #         print("ores.wmflabs.org responded: " + str(r))
        #         r = r.json()
        #         qualityDict = r[str(revisionID)]
        #         innerIndex = 0
        #         while 'prediction' not in qualityDict and innerIndex < 4:
        #             qualityDict = qualityDict['score']
        #             innerIndex = innerIndex + 1
        #             print("Found score in qualityDict for the " +
        #                   str(innerIndex) + " time.")
        #         qualityClass = qualityDict['prediction']
        #         break
        #     except:
        #         print(
        #             "\n\n\nI cannot retrieve the class of this article from the API! Error Message: " + str(e))
        #         time.sleep(1)

        # probabilitiesOfEachClass = qualityDict['probability']
        # FAClassProbability = probabilitiesOfEachClass['FA']
        # GAClassProbability = probabilitiesOfEachClass['GA']
        # BClassProbability = probabilitiesOfEachClass['B']
        # CClassProbability = probabilitiesOfEachClass['C']
        # StartClassProbability = probabilitiesOfEachClass['Start']
        # StubClassProbability = probabilitiesOfEachClass['Stub']

        # weightedAverage = (float(StubClassProbability) + 2 * float(StartClassProbability) + 3 * float(CClassProbability) +
        #                    4 * float(BClassProbability) + 5 * float(GAClassProbability) + 6 * float(FAClassProbability)) / (
        #     float(StubClassProbability) + float(StartClassProbability) + float(CClassProbability) +
        #     float(BClassProbability) + float(GAClassProbability) + float(FAClassProbability))

        # if weightedAverage > 5:
        #     qualityClass = "FA-Class"
        # elif weightedAverage > 4:
        #     qualityClass = "GA-Class"
        # elif weightedAverage > 3:
        #     qualityClass = "B-Class"
        # elif weightedAverage > 2:
        #     qualityClass = "C-Class"
        # elif weightedAverage > 1:
        #     qualityClass = "Start-Class"
        # else:
        #     qualityClass = "Stub-Class"

        # print("qualityClass: " + qualityClass)

    if talkSoup != '' and talkSoup.find('div', id="catlinks") != None and talkSoup.find('b', text="Wikipedia does not have a") == None:
        categoryDIVTag = talkSoup.find('div', id="catlinks")

        if categoryDIVTag.find(text=re.compile('.*FA-Class.*')) != None:
            qualityClass = "FA-Class"

        elif categoryDIVTag.find(text=re.compile('.* A-Class.*')) != None:
            qualityClass = "A-Class"

        elif categoryDIVTag.find(text=re.compile('.*GA-Class.*')) != None:
            qualityClass = "GA-Class"

        elif categoryDIVTag.find(text=re.compile('.*B+ class.*')) != None:
            qualityClass = "B+ class"

        elif categoryDIVTag.find(text=re.compile('.*B-Class.*')) != None:
            qualityClass = "B-Class"

        elif categoryDIVTag.find(text=re.compile('.*C-Class.*')) != None:
            qualityClass = "C-Class"

        elif categoryDIVTag.find(text=re.compile('.*Stub-Class.*')) != None:
            qualityClass = "Stub-Class"

        if categoryDIVTag.find(text=re.compile('.*Top-importance.*')) != None:
            importanceClass = "Top-importance"

        elif categoryDIVTag.find(text=re.compile('.*High-importance.*')) != None:
            importanceClass = "High-importance"

        elif categoryDIVTag.find(text=re.compile('.*Mid-importance.*')) != None:
            importanceClass = "Mid-importancee"

        elif categoryDIVTag.find(text=re.compile('.*Low-importance.*')) != None:
            importanceClass = "Low-importance"

        elif categoryDIVTag.find(text=re.compile('.*NA-importance.*')) != None:
            importanceClass = "NA-importance"

        elif categoryDIVTag.find(text=re.compile('.*Unknown-importance.*')) != None:
            importanceClass = "Unknown-importance"

        elif categoryDIVTag.find(text=re.compile('.*Bottom-importance.*')) != None:
            importanceClass = "Bottom-importance"

        if desiredCategory.lower() in categoryDIVTag.prettify().lower():
            desiredCategoryFound = True

    return qualityClass, importanceClass, desiredCategoryFound


def WikipediaPageStats(articleHyperlink, articleSoup, articleTitle, desiredCategory):

    print("Wikipedia article title before correction:", articleTitle)

    appropriateArticleTitle = re.search("(.+) -", articleTitle)

    if appropriateArticleTitle != None:

        articleTitle = appropriateArticleTitle.group(1)

    print("Wikipedia article title after correction:", articleTitle)

    articleEncodedTitles = re.findall(
        "(?:wiki/([^?]+))|(?:title=([^&]+))", articleHyperlink)

    print("Wikipedia articles' Encoded Titles:", articleEncodedTitles)

    if articleEncodedTitles[0][0] != '':

        articleEncodedTitle = articleEncodedTitles[0][0]

    elif articleEncodedTitles[0][1] != '':

        articleEncodedTitle = articleEncodedTitles[0][1]

    elif articleEncodedTitles[1][0] != '':

        articleEncodedTitle = articleEncodedTitles[1][0]

    elif articleEncodedTitles[1][1] != '':

        articleEncodedTitle = articleEncodedTitles[1][1]

    print("Encoded title of the article: " + articleEncodedTitle)

    # if '%E2%80%93' in articleEncodedTitle:
    #   strObjs = articleEncodedTitle.split('%E2%80%93')
    #   articleEncodedTitle = strObj[0]
    #   for index in range(len(strObjs)):
    #       articleEncodedTitle += u'–' + strObjs[index]
    # articleEncodedTitle = articleEncodedTitle.replace('%2F', '/')
    # articleEncodedTitle = articleEncodedTitle.replace('%3F', '?')
    # articleEncodedTitle = articleEncodedTitle.replace('%27', "&")
    # articleEncodedTitle = articleEncodedTitle.replace('%27', "'")
    # articleEncodedTitle = articleEncodedTitle.replace('%28', '(')
    # articleEncodedTitle = articleEncodedTitle.replace('%29', ')')
    # articleEncodedTitle = articleEncodedTitle.replace('%E2%80%93', u'–')

    articleEncodedTitle = unquote(articleEncodedTitle)

    responseCounter = 0
    numberOfExternalLinks = 0
    # for result in GETRequestFromWikipedia( {'titles':articleTitle, 'prop':'info|contributors|revisions', 'inprop':'protection|watchers', 'pclimit':'max', 'rvprop':'timestamp', 'rvlimit':'max'} ):
    for result in GETRequestFromWikipedia({'titles': articleEncodedTitle, 'prop': 'info|extlinks', 'inprop': 'protection|watchers', 'ellimit': 'max'}):

        # if result != [ ]:
        pageData = list(result['pages'].values())[0]

        qualityClass, importanceClass, desiredCategoryFound = classFinder(
            articleHyperlink, articleEncodedTitle, desiredCategory)

        if 'pageid' in pageData and pageData['ns'] == 0:
                # if 'pageid' in pageData and pageData['ns'] == 0 and desiredCategoryFound == True:

            if responseCounter == 0:

                    # pageInfoData = result['pages'].values()[0]

                print("\n\nID: " + str(pageData['pageid']), '\n')

                statsContext = {}
                statsContext['pageid'] = pageData['pageid']
                statsContext['title'] = articleTitle

                editProtectionLevel = 'None'

                for protection in pageData['protection']:
                    if protection['type'] == 'edit':
                        editProtectionLevel = protection['level']
                        break

                statsContext['editProtectionLevel'] = editProtectionLevel

                if num(pageData['length']) < 1500:
                    print(
                        "The length of the article is less than 1500 characters, consider the page as a stub. Do not recommend it.")
                    qualityClass = "Stub-Class"

                statsContext['qualityClass'] = qualityClass

                statsContext['importanceClass'] = importanceClass

                statsContext['length'] = pageData['length']

                watchersNumber = '0'
                if 'watchers' in pageData:
                    watchersNumber = str(pageData['watchers'])

                statsContext['watchersNumber'] = watchersNumber

                statsContext['touched'] = pageData['touched']

                infoURL = "http://en.wikipedia.org/w/index.php?title=" + \
                    articleEncodedTitle + "&action=info"

                infoSoup = scrapeWebsite(
                    infoURL, 'tr', 'id', "mw-pageinfo-watchers", "", "", "")

                if infoSoup != False:

                    redirectsStatisticsTag = infoSoup.find(
                        'tr', id="mw-pageinfo-watchers").findNext('tr')
                    redirectsStatisticsNumber = '0'
                    if redirectsStatisticsTag:
                        redirectsStatisticsNumber = redirectsStatisticsTag.findAll('td')[
                            1].renderContents()

                    statsContext['redirects'] = redirectsStatisticsNumber

                    firsttimeStatisticsTag = infoSoup.find(
                        'tr', id="mw-pageinfo-firsttime")
                    firsttimeStatisticsNumber = '0'
                    if firsttimeStatisticsTag:
                        firsttimeStatisticsNumber = firsttimeStatisticsTag.findAll(
                            'td')[1].find('a').renderContents()

                    statsContext['creationDate'] = firsttimeStatisticsNumber

                    editsStatisticsTag = infoSoup.find(
                        'tr', id="mw-pageinfo-edits")
                    editsStatisticsNumber = '0'
                    if editsStatisticsTag:
                        editsStatisticsNumber = editsStatisticsTag.findAll('td')[
                            1].renderContents()

                    statsContext['editsNum'] = editsStatisticsNumber

                    # authorsStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-authors")
                    # authorsStatisticsNumber = '0'
                    # if authorsStatisticsTag:
                    #     authorsStatisticsNumber = authorsStatisticsTag.findAll('td')[1].renderContents()

                    # statsContext['distinctAuthors'] = authorsStatisticsNumber

                    recentEditsStatisticsTag = infoSoup.find(
                        'tr', id="mw-pageinfo-recent-edits")
                    recentEditsStatisticsNumber = '0'
                    if recentEditsStatisticsTag:
                        recentEditsStatisticsNumber = recentEditsStatisticsTag.findAll('td')[
                            1].renderContents()

                    statsContext['recentEdits'] = recentEditsStatisticsNumber

                    recentAuthorsStatisticsTag = infoSoup.find(
                        'tr', id="mw-pageinfo-recent-authors")
                    recentAuthorsStatisticsNumber = '0'
                    if recentAuthorsStatisticsTag:
                        recentAuthorsStatisticsNumber = recentAuthorsStatisticsTag.findAll('td')[
                            1].renderContents()

                    statsContext['recentDistinctAuthors'] = recentAuthorsStatisticsNumber

                else:
                    statsContext['redirects'] = ''
                    statsContext['creationDate'] = ''
                    statsContext['editsNum'] = ''
                    # statsContext['distinctAuthors'] = ''
                    statsContext['recentEdits'] = ''
                    statsContext['recentDistinctAuthors'] = ''

                # rhStatisticsURL = "http://tools.wmflabs.org/xtools/articleinfo/index.php?article=" + articleEncodedTitle + "&lang=en&wiki=wikipedia"
                # rhStatisticsSoup = scrapeWebsite(rhStatisticsURL, 'div', 'id', "generalstats", "p", "class", "alert alert-danger xt-alert")

                # if rhStatisticsSoup != False and rhStatisticsSoup != "No Search Result":
                #     generalstatsContainer = rhStatisticsSoup.find('div', id="generalstats").find('tr').findAll('tr')
                #     submitAndPrint (statsFile, "Number of minor edits: ", re.search('(\d+) ', generalstatsContainer[6].findAll('td')[1].renderContents()).group(1))
                #     submitAndPrint (statsFile, "Average time between edits: ", generalstatsContainer[10].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Average number of edits per month: ", generalstatsContainer[12].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Average number of edits per year: ", generalstatsContainer[13].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Number of edits in the past 24 hours: ", generalstatsContainer[15].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Number of edits in the past 7 days: ", generalstatsContainer[16].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Number of edits in the past 30 days: ", generalstatsContainer[17].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Number of edits in the past 365 days: ", generalstatsContainer[18].findAll('td')[1].renderContents())
                #     submitAndPrint (statsFile, "Number of links to this page: ", generalstatsContainer[27].findAll('td')[1].find('a').renderContents())
                # else:
                #     submitAndPrint (statsFile, "Number of minor edits: ", '')
                #     submitAndPrint (statsFile, "Average time between edits: ", '')
                #     submitAndPrint (statsFile, "Average number of edits per month: ", '')
                #     submitAndPrint (statsFile, "Average number of edits per year: ", '')
                #     submitAndPrint (statsFile, "Number of edits in the the past 24 hours: ", '')
                #     submitAndPrint (statsFile, "Number of edits in the past 7 days: ", '')
                #     submitAndPrint (statsFile, "Number of edits in the past 30 days: ", '')
                #     submitAndPrint (statsFile, "Number of edits in the past 365 days: ", '')
                #     submitAndPrint (statsFile, "Number of links to this page: ", '')

                todayDate = (datetime.date.today()).strftime('%Y%m%d')
                pastMonthDate = (datetime.date.today() -
                                 datetime.timedelta(days=30)).strftime('%Y%m%d')
                trafficStatisticsURL = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/" +
                                        "all-access/user/" + articleEncodedTitle.replace("/", "-") + "/daily/" +
                                        pastMonthDate + "/" + todayDate)
                viewsErrorsNum = 0
                while viewsErrorsNum < 10:
                    try:
                        print("Requesting " + trafficStatisticsURL)
                    except:
                        print(
                            "UnicodeEncodeError: 'ascii' codec can't encode character.")
                    try:
                        numberofViewsResponse = requests.get(
                            trafficStatisticsURL)
                        numberofViewsResponse = numberofViewsResponse.json()
                        numberofViewsPerDays = numberofViewsResponse['items']
                        break
                    except:
                        print(
                            "\n\n\nI cannot retrieve the number of views of this article!")
                        time.sleep(1)
                        viewsErrorsNum += 1
                viewsNum = 0
                if viewsErrorsNum < 10:
                    for numberofViewsPerDay in numberofViewsPerDays:
                        viewsNum += numberofViewsPerDay['views']

                statsContext['viewsNum'] = viewsNum
                print("# of views in the last month: " + str(viewsNum))

                if articleSoup != False:
                    referenceList = articleSoup.findAll(
                        'li', id=re.compile('cite_note.*'))
                    statsContext['referencesNum'] = len(referenceList)
                    # if referenceList != None:
                    #     referenceList = referenceList.findAll('li')
                    # else:
                    #     referenceList = [ ]
                    afterYear = 2010
                    referencesNumber = 0
                    for reference in referenceList:
                        yearDigits = re.search(
                            '.*(\d\d\d\d).*', str(reference.renderContents()))
                        if yearDigits != None and int(yearDigits.group(1)) >= afterYear:
                            referencesNumber += 1
                    statsContext['referencesNumAfter2010'] = referencesNumber
                else:
                    statsContext['referencesNum'] = '0'
                    statsContext['referencesNumAfter2010'] = '0'
                if 'extlinks' in pageData:
                    numberOfExternalLinks = len(pageData['extlinks'])
            else:
                if 'extlinks' in pageData:
                    numberOfExternalLinks += len(pageData['extlinks'])
            responseCounter = 1
            print("# External Hyperlinks: " + str(numberOfExternalLinks), '\n')

            statsContext['externalLinks'] = numberOfExternalLinks
            return statsContext
        else:
            return []


# Receive Wikipedia pages recommendations file and generate Wikipedia pages' stats file.
def WikipediaStatsGenerator(recommendationsFile):

    previousURLs = []

    with open(recommendationsFile + '.csv', 'rb') as fr:
        reader = csv.reader(fr)

        with open(recommendationsFile + '_Stats.csv', 'wb') as fw:
            writer = csv.writer(fw)

            pubResultRow = ['ID', 'Title', 'Edit Protection Level', 'Class', 'Importance', 'Page Length', '# watchers', 'Time of Last Edit', '# redirects to this page', 'Page Creation Date', 'Total # edits',
                            'Recent # edits (within past 30 days)', 'Recent # distinct authors', '# views (last 90 days)', 'Total # references', '# references published after 2010', '# External Hyperlinks']
            writer.writerow(pubResultRow)

            header = next(reader)
            for row in reader:
                for i in range(2, len(row) - 1, 3):
                    if row[i] != "" and row[i+1] != "":
                        wikipageTitle = row[i]
                        print("Wikipage Title:", wikipageTitle)
                        wikipageURL = row[i+1]
                        print("Wikipage URL:", wikipageURL)
                        wikipediaSoup = soupStructure(wikipageURL)
                        print("Soup is Retrieved.")

                        if wikipediaSoup != "" and not wikipageURL in previousURLs:
                            pubResultRow = WikipediaPageStats(
                                wikipageURL, wikipediaSoup, wikipageTitle, 'Econ')

                            trialNum = 0
                            while pubResultRow == [] and trialNum < 10:
                                trialNum += 1
                                # print("wikipageURL:", wikipageURL, "is not found. Please enter a new one:")
                                # wikipageURL = input()
                                pubResultRow = WikipediaPageStats(
                                    wikipageURL, wikipediaSoup, wikipageTitle, 'Econ')

                            print(pubResultRow)
                            writer.writerow(pubResultRow)
                            previousURLs.append(wikipageURL)


# To convert a Unicode URL to ASCII (UTF-8 percent-escaped).
def fixurl(url):
    if not isinstance(url, unicode):
        url = url.decode('utf8')
    parsed = urlparse.urlsplit(url)
    userpass, at, hostport = parsed.netloc.rpartition('@')
    user, colon1, pass_ = userpass.partition(':')
    host, colon2, port = hostport.partition(':')
    scheme = parsed.scheme.encode('utf8')
    user = quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        quote(unquote(pce).encode('utf8'), '')
        for pce in parsed.path.split('/')
    )
    query = quote(unquote(parsed.query).encode('utf8'), '=&?/')
    fragment = quote(unquote(parsed.fragment).encode('utf8'))
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urlunsplit((scheme, netloc, path, query, fragment))


def findWikiprojectNumOfViews(WikiprojectEncodedTitle="WikiProject_Economics"):

    with open(WikiprojectEncodedTitle + '_Pages_Views.csv', 'wb') as fw:
        writer = csv.writer(fw)

        pubResultRow = ['WikiprojectTitle', 'Page Id',
                        'Page Title', '# views (last 90 days)']
        writer.writerow(pubResultRow)
        pagesReqParameteres = {'project': WikiprojectEncodedTitle}
        pagesReqURL = "https://alahele.ischool.uw.edu:8997/api/getProjectPages?" + \
            urllib.urlencode(pagesReqParameteres)

        print(pagesReqURL)
        responseNotRetrieved = True
        pagesResponse = {}
        pageDataList = {}

        TotalPagesViews = 0
        TotalPagesNum = 0
        errorNumber = 0
        while responseNotRetrieved and errorNumber <= 10:
            try:
                pagesResponseJSON = requests.get(
                    pagesReqURL, verify=False, timeout=1000)
                pagesResponse = pagesResponseJSON.json()
                errorstatusAttribute = pagesResponse['errorstatus']
                if errorstatusAttribute == 'success':
                    responseNotRetrieved = False

            except(e):
                errorNumber += 1
                print("An exception occurred: " + str(e))
                time.sleep(4)
        if errorNumber >= 10:
            print("I am not able to request this page from Alahele server.")
            input()
        if len(pagesResponse['result'].keys()) != 0:
            pageDataList = pagesResponse['result'][WikiprojectEncodedTitle]
            for pageData in pageDataList:
                pageEncodedTitle = pageData['tp_title']
                pageEncodedTitle = fixurl(pageEncodedTitle)

                if "WikiProject_" in pageEncodedTitle:
                    pageEncodedTitle = "Wikipedia:" + pageEncodedTitle
                print("Page Title:", pageEncodedTitle)
                pageID = pageData['pp_id']
                print("Page ID:", pageID)
                trafficStatisticsURL = "http://stats.grok.se/en/latest90/" + pageEncodedTitle
                trafficStatisticsSoup = scrapeWebsite(
                    trafficStatisticsURL, 'p', '', '', "", "", "")

                if trafficStatisticsSoup != False:
                    trafficPTag = strip_tags(trafficStatisticsSoup.find(
                        'p').renderContents().decode('utf-8'))
                viewsOverPastNinetyDays = re.search(
                    '.*has been viewed (\d*).*', trafficPTag).group(1)

                print("# Views:", viewsOverPastNinetyDays)
                writer.writerow([WikiprojectEncodedTitle.encode(
                    'utf-8'), pageID, pageEncodedTitle.encode('utf-8'), viewsOverPastNinetyDays])

                TotalPagesViews = num(viewsOverPastNinetyDays)
                TotalPagesNum += 1

        print("Average # Views over the past 90 days:",
              (TotalPagesViews / TotalPagesNum))


def IsWikipageAppropriate(title, hyperlink):

    if ("Category:" in title or "User:" in title or "Talk:" in title or "User talk:" in title or
            "Book:" in title or "Template:" in title):
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
        # if resultRow[2].lower() != "none":
        #     print("The Wikipedia page is edit protected. Do not recommend it.")
        #     return False, None
        if resultRow['qualityClass'].lower() == "stub-class" or resultRow['qualityClass'].lower() == "start":
            print("The Wikipedia page is a " +
                  resultRow['qualityClass'] + ". Do not recommend it.")
            return False, None
        if resultRow['importanceClass'].lower() != 'high-importance' and resultRow['importanceClass'].lower() != 'top-importance':
            print("The Wikipedia page is a " +
                  resultRow['importanceClass'] + ". Do not recommend it.")
            return False, None
        if num(resultRow['length']) < 1000:
            print(
                "The Wikipedia page has been viewed less than 1000 times. Do not recommend it.")
            return False, None

        print("The Wikipedia page is OK to recommend.")
        return True, resultRow


print(IsWikipageAppropriate("Epidemiology of attention deficit hyperactive disorder",
                            "https://en.wikipedia.org/wiki/Epidemiology_of_attention_deficit_hyperactive_disorder"))
