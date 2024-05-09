from django.http import JsonResponse
from django.shortcuts import render,redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import requests
from bs4 import BeautifulSoup as bs
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# Create your views here.
@api_view(['GET'])
def home(r):
    return Response({"hes":"ee"})

class SignupView(APIView):
    def post(self,r):
        serializer = UserSerializer(data=r.data)
        if serializer.is_valid():
            user=serializer.save()
            token,created=Token.objects.get_or_create(user=user)
            return Response({"token":token.key,"created":created,"status":True},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    def post(self,r):
        serializer = LoginSerializer(data=r.data)
        if serializer.is_valid():
            try:
                user=User.objects.get(email=serializer.data["email"].lower())
                user=authenticate(username=user.username,password=serializer.data['password'])
                if user is not None:
                    token,created=Token.objects.get_or_create(user=user)
                    return Response({"token":token.key,"created":created,"status":True},status=status.HTTP_200_OK)
                return  Response({"error":"Invalid Credentials"},status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error":"User not found with this email"},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class SignOutView(APIView):
    authentication_classes=[TokenAuthentication]
    def get(self,r):
        Token.objects.get(key=r.auth).delete()
        return Response({"status":True},status=status.HTTP_200_OK)
class SearchView(APIView):
    def get(self,r):
        search=r.GET['link']
        query=search.split('/')
        if "amazon" in search or "flipkart" in search:
            try:
                query=query[3]
            except:
                query=search
        else:
            query=search
        api="AIzaSyBTBPefOCsWFb81iniVafHQPY9a5Qp78fg"
        id="50c64307680f64482"
        params={
                "q":query,
                "key":api,
                'cx':id
            }
        req=requests.get("https://www.googleapis.com/customsearch/v1",params=params)
        data=req.json()
        if int(data["searchInformation"]["totalResults"])>0:
            for i in data['items']:
                i['link']=i['link'].replace("https://pricehistoryapp.com/product/","")
        return Response(data,status=status.HTTP_200_OK)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestView(APIView):
    def get(self, request):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://pricehistoryapp.com/")

        # Wait for the search input field to be clickable
        search_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input'))
        )

        search_input.send_keys("firebolt phoenix amoled")
        search_input.send_keys(Keys.ENTER)

        # Wait for page to load (add more explicit waits as needed)
        time.sleep(5)

        # Now you can interact with the page or extract data
        # For example, you can get the page source:
        # page_source = driver.page_source
        soup=bs(driver.page_source,'html.parser')
        data=soup.find('div',id='___gcse_0')
        data=json.dumps({'html_content': str(data)}, ensure_ascii=False)
        driver.quit()

        return Response(data)

# class TestView(APIView):
#     def get(self,r):
#         driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#         driver.get("https://pricehistoryapp.com/")
#         time.sleep(5)
#         search=driver.find_element_by_xpath('//input')
#         search.send_keys("firebolt phoenix amoled")
#         search.send_keys(Keys.ENTER)
#         # soup=bs(driver.page_source,'html.parser')
#         # print(soup)
#         return Response({"status":True})
class ProductView(APIView):
    def get(self,r):
        req=requests.get("https://pricehistoryapp.com/product/"+r.GET['link'])
        soup=bs(req.content,'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        try:
            script_content = script.string    
            data = json.loads(script_content)
            data = data.get('props', {}).get('pageProps', {})  
            return Response(data["ogProduct"],status=status.HTTP_200_OK)    
        except:
            return Response({"status":False},status=status.HTTP_400_BAD_REQUEST)
class AddProduct(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,r):
        pass


