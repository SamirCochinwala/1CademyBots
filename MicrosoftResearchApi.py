import json
import requests
import MicrosoftAcademicAPIKey
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



def getExpression(query, count='1'):
    interpret_params = {
            'query': query,
            'complete': '1',
            'count': count
            }

    try:
        request = requests.get(INTERPRET_URL, params=interpret_params, headers=headers)
        result = request.json()
        result = result['interpretations']  # loop the result if request more than 1 count
        result = result[0]

        # get the expression for evaluating and getting entity
        expression = result['rules'][0]['output']['value']
        return expression
    except Exception as e:
        print('The error message is ' + str(e))


def getEntity(expression, count='1', attributes='Ti'):
    evaluate_params = {
        'expr': expression,
        'count': count,
        'attributes': attributes
    }

    try:
        request = requests.get(
            EVALUATE_URL, params=evaluate_params, headers=headers)
        result = request.json()
        # print(result)
        result = result['entities'][0]  # loop the result if request more than 1 count

        title = result['Ti']
        # citation_count = result['CC']
        authors = [list(item.values())[0] for item in result['AA']]
        key_word = [list(item.values())[0] for item in result['F']]
        abstract_indexes = result['IA']['InvertedIndex']
        abs_words_dict = {}
        for k,v in abstract_indexes.items():
            for index in v:
                abs_words_dict[index]=k

        sorted_list = [item[1] for item in sorted(abs_words_dict.items())]
        abstract = ' '.join(sorted_list)

        return title, authors, key_word, abstract

    except Exception as e:
        print('The error message is ' + str(e))

if __name__ == '__main__':
    query = input('What do you want to search?\n')
    expression = getExpression(query)
    title, authors, key_word, abstract = getEntity(
        expression, attributes='Ti,AA.DAuN,IA,CC,F.FN')

    print('Title: ', title)
    print("Authors: ", authors)
    print('Key Words: ', key_word)
    print('Abstract: ', abstract)
