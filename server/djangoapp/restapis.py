import requests
import logging
import json

from requests.api import request
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1  import Features, SentimentOptions



# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url,  **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        #if 'api_key' in kwargs.keys:
         #   response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},       auth=HTTPBasicAuth('apikey', kwargs['api_key'] ))
        #else:
        
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)

        json_data = json.loads(response.text)
        
        return json_data                            

        
    except:
        # If any error occurs

        print("Network exception occurred")
        status_code = response.status_code
        print("With status {} ".format(status_code))
    
    



# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    try: # for Python 3
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)

    requests_log.propagate = True

    headers = {'Content-type': 'application/json'}
    #json_payload =  {}
    #json_payload["t1"] = "teszt";
    #print("json_payload\n\n")
    #print(json_payload)
    #print("----------------------------\n\n")
    
    try:
        response = requests.post(url, json=json_payload, headers=headers)
        #print(response )
    except:
        # If any error occurs

        print("Network exception occurred")
        status_code = response.status_code
        print("With status {} ".format(status_code))
    


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        #print(dealers)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], full_name=dealer_doc["full_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list


def get_dealer_reviews_from_cf(url, dealer_id,  **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId = dealer_id)
    #print(json_result)
    if json_result:
        # Get the row list in JSON as dealers
       reviews = json_result['entries']
       print("------------------------------------\n")
       print(reviews)
        
       for review in reviews:
        
           review_doc = review

           if "car_year"  not in review_doc.keys():
                review_doc["car_year"] = ""
           if "car_make"  not in review_doc.keys():
                review_doc["car_model"] = ""     
           if "car_make"  not in review_doc.keys():
                review_doc["car_make"] = ""
           if "purchase_date"  not in review_doc.keys():
                review_doc["purchase_date"] = ""
        
           review_obj = DealerReview(dealership = review_doc["dealership"],  name = review_doc["name"],   purchase = review_doc["purchase"],  review = review_doc["review"],     purchase_date = review_doc["purchase_date"],     car_make = review_doc["car_make"],     car_model = review_doc["car_model"],     car_year = review_doc["car_year"],     sentiment = "",     id = review_doc["id"] );

           review_obj.sentiment = analyze_review_sentiments(review_obj.review)   
           results.append(review_obj)
       return results


    



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(dealerreview):

    api_key  =  'aeTwGNkBiaWt6EX-PagfARYlLsmNPq_k7IhPr0XUxETj'
    url= 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/0642a3b4-3ca7-4e5d-80c3-d642010acbd2'  
    '''
    params = dict()
    params["text"] = kwargs["text"]
    params["version"] = kwargs["version"]
    params["features"] = kwargs["features"]
    params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
    '''  
    authenticator = IAMAuthenticator(api_key)

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2020-08-01',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)
      
   
    
    try:
        response = natural_language_understanding.analyze(
            text = dealerreview,
            features=Features(sentiment=SentimentOptions())).get_result() 
        return response['sentiment']['document']['label']  
    except:
        return "neutral"

    
def get_dealer_name(did):
    url = "https://675e0886.eu-gb.apigw.appdomain.cloud/api/dealer/?id="+str(did)
    result = ""
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        #print(dealers)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            
            # Create a CarDealer object with values in `doc` object
            result= dealer["full_name"]

    return result





