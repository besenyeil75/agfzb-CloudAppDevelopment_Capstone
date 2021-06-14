import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1  import Features, SentimentOptions

authenticator = IAMAuthenticator('aeTwGNkBiaWt6EX-PagfARYlLsmNPq_k7IhPr0XUxETj')

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2020-08-01',
    authenticator=authenticator
)

natural_language_understanding.set_service_url('https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/0642a3b4-3ca7-4e5d-80c3-d642010acbd2')
     

response = natural_language_understanding.analyze(
    url='www.wsj.com/news/markets',
    features=Features(sentiment=SentimentOptions())).get_result() 

print(json.dumps(response, indent=2))


'''
See the SentimentResult object in the Analyze text method.

Example Sentiment feature response

{
  "usage": {
    "text_units": 1,
    "text_characters": 1188,
    "features": 1
  },
  "sentiment": {
    "targets": [
      {
        "text": "stocks",
        "score": 0.279964,
        "label": "positive"
      }
    ],
    "document": {
      "score": 0.127034,
      "label": "positive"
    }
  },
  "retrieved_url": "https://www.wsj.com/news/markets",
  "language": "en"
}

Syntax
'''