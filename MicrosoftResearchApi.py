from datetime import date
import json
import requests
import MicrosoftAcademicAPIKey
import csv
# import http.client
# import urllib.request
# import urllib.parse
# import urllib.error
# import base64


client_key = MicrosoftAcademicAPIKey.API_KEY

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': client_key,
}

EVALUATE_URL = 'https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate'
INTERPRET_URL = 'https://api.labs.cognitive.microsoft.com/academic/v1.0/interpret'

CACHE_DICT = {}
CACHE_FILE = 'MicrosoftAcademicPaperCache.json'

CSV_HEADER = ['id', 'title', 'authors', 'key_words', 'abstract', 'venue', 'doi', 'citation']


def open_cache(file_name):
    try:
        # print('Opening cache...')
        cache_file = open(file_name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, file_name):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(file_name, "w")
    fw.write(dumped_json_cache)
    fw.close()


def write_csv(paper_id, title, authors, key_words, abstract, venue, doi, citation):
    try:
        with open('MicrosoftAcademicPapers.csv', 'r', newline='') as csvfile:
            with open('MicrosoftAcademicPapers.csv', 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
                writer.writerow({'id': paper_id, 'title': title, 'authors': authors,
                                'key_words': key_words, 'abstract': abstract, 'venue': venue,
                                'doi': doi, 'citation': citation})
    except:
        with open('MicrosoftAcademicPapers.csv', 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
                writer.writeheader()
                writer.writerow({'id': paper_id, 'title': title, 'authors': authors,
                                 'key_words': key_words, 'abstract': abstract, 'venue': venue,
                                 'doi': doi, 'citation': citation})



def getExpression(query):
    interpret_params = {
            'query': query,
            'complete': '1',
            'count': '1', # get the most related expression
            }

    try:
        request = requests.get(INTERPRET_URL, params=interpret_params, headers=headers)
        result = request.json()
        result = result['interpretations']
        result = result[0]

        # get the expression for evaluating and getting entity
        expression = result['rules'][0]['output']['value']

        # add today's date to the expression to get the latest articles
        date_of_today = str(date.today())
        d = f"D='{date_of_today}'"
        expression = f'And({expression}, {d})'
        return expression
    except Exception as e:
        print('The error message is ' + str(e))


def getEntity(expression, count='1', attributes='Ti'):

    evaluate_params = {
        'expr': expression,
        'count': count,
        'attributes': attributes,
        # 'offset': offset
    }

    try:
        request = requests.get(
            EVALUATE_URL, params=evaluate_params, headers=headers)
        result = request.json()
        result = result['entities']  # loop the result if request more than 1 count

        for entity in result:
            paper_id = str(entity['Id'])
            if paper_id in CACHE_DICT.keys():
                pass
            else:
                CACHE_DICT[paper_id]=entity
                title = entity['Ti']
                # print(title)
                authors = [list(item.values())[0] for item in entity['AA']]
                key_words = [list(item.values())[0] for item in entity['F']]
                # publication_type = entity['Pt']

                try:
                    abstract_indexes = entity['IA']['InvertedIndex']
                    abs_words_dict = {}
                    for k,v in abstract_indexes.items():
                        for index in v:
                            abs_words_dict[index]=k
                    sorted_list = [item[1] for item in sorted(abs_words_dict.items())]
                    abstract = ' '.join(sorted_list)
                except:
                    abstract = 'No record'

                # publisher = entity['PB']
                # citation = entity['CitCon'] #return None
                try:
                    venue = entity['VFN']
                except:
                    venue = 'No record'
                try:
                    doi = entity['DOI']
                except:
                    doi = 'No record'
                # print(result)
                citation = ''

                # write data to csv

                write_csv(paper_id, title, authors, key_words,
                            abstract, venue, doi, citation)

                save_cache(CACHE_DICT, CACHE_FILE)

        # return paper_id, title, authors, key_words, abstract, venue, doi

    except Exception as e:
        print('The error message is ' + str(e))


if __name__ == "__main__":
    count = 3
else:
    count = 50

query = input('What do you want to search?\n')
CACHE_DICT = open_cache(CACHE_FILE)
expression = getExpression(query)

getEntity(
        expression, count=count, attributes='Id,Ti,AA.DAuN,IA,F.FN,VFN,DOI,Pt')

# print('Title: ', title)
# print("Authors: ", authors)
# print('Key Words: ', key_words)
# print('Abstract: ', abstract)
# # print('Publisher: ', publisher)
# print('Journal Venue: ', venue)
# print('DOI: ', doi)
# print('Paper ID: ', )
