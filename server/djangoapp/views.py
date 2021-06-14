from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarMake
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_name
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:get_dealerships')
        else:
            # If not, return to login page again
            #return render(request, 'djangoapp:get_dealerships', context)
            return redirect('djangoapp:get_dealerships')
    else:
        return render(request, 'djangoapp:get_dealerships', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:get_dealerships')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        
         
        username = request.POST['user_name']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(

                username = username, 
                password = password,
                first_name = first_name,
                last_name = last_name
            )#<HINT> create the user with above info
            # <HINT> Login the user and 
            # redirect to course list page
            return redirect("djangoapp:get_dealerships")
        else:
            return render(request, 'djangoapp:registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    print("\n\nrequest.method  "+  request.method+ "\n\n")
    if request.method == "GET":
        url = "https://675e0886.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context  = {}
        context['dealership_list']  = dealerships

        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...


def get_dealer_details(request, dealer_id): 
    url = "https://675e0886.eu-gb.apigw.appdomain.cloud/api/review?dealerId?" + str(dealer_id)
        # Get dealers from the URL
    reviews = get_dealer_reviews_from_cf(url, dealer_id)

    
    
    context  = {}
    context['review_list']  = reviews
    context['dealer_id']  = dealer_id
    
    full_name  = get_dealer_name(dealer_id)
    context['full_name']  = full_name

    #print(context)
    return render(request, 'djangoapp/dealer_details.html', context)
    #TODO
    # view to also print sentiment for each review: 
    #  and append a list of reviews to context and return a HttpResponse, 





def add_review(request, dealer_id):
    
    if request.user.is_authenticated:
        if request.method ==  'GET': 
            
            cms = CarModel.objects.filter(DealerId =dealer_id ) 
            
            
            context = {}
            context['dealer_id']  = dealer_id
            context['cars']  = cms.all()
            full_name  = get_dealer_name(dealer_id)
            context['full_name']  = full_name


            return render(request, 'djangoapp/add_review.html', context)
            

        if  request.method == 'POST':
                review = {}
                review['id']  = str(uuid.uuid1())  
                review["purchase_date"] = datetime.utcnow().isoformat()
                review["dealership"] = int(request.POST.get("dealer_id"))
                review["review"] = request.POST.get("content")
                
                car = CarModel.objects.filter(pk = request.POST["car"] ).get()
                #print(car)
                review["car_make"] =  car.carmake.name
                review["car_model"] =  car.name
                review["car_year"] =  int(car.year.strftime("%Y"))
                review["name"] = request.user.username
                review["purchase"] = False
                if request.POST.get('purchasecheck') == 'on':
                    review["purchase"] = True

                #dealer = CarModel.objects.filter(DealerId = request.POST["car"] ) .get()

                print(review);
                json_payload  = {} 
                json_payload["review"] = review
                                                 
                url = "https://675e0886.eu-gb.apigw.appdomain.cloud/api/review-post"
                res = post_request(url, json_payload, dealerId=dealer_id)

                #print(res)
                return redirect("djangoapp:get_dealership_reviews", dealer_id=dealer_id)
                

            
            #For purchase, you may use car.year.strftime("%Y") to only get the year from the date field.

            
            
            
    



