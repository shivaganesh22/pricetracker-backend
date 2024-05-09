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
        try:
            Token.objects.get(key=r.auth).delete()
            return Response({"status":True},status=status.HTTP_200_OK)
        except:
            return Response({"status":False,"error":"Failed to logout"},status=status.HTTP_400_BAD_REQUEST)
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
        try:
            for i in data['items']:
                i['link']=i['link'].replace("https://pricehistoryapp.com/product/","")
        except :
            pass
        return Response(data,status=status.HTTP_200_OK)

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


