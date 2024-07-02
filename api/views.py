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
from django.core.mail import send_mail
import uuid
# Create your views here.

def home(r):
    if r.method=="POST":
        img=r.FILES['img']
        ImageUpload(img=img).save()
        return redirect('/')
    return render(r,'home.html')
def sendMail(subject,message,email):
    send_mail(subject,message,'rsgtracker@gmail.com',email,fail_silently=False)

class SignupView(APIView):
    def post(self,r):
        serializer = UserSerializer(data=r.data)
        if serializer.is_valid():
            user=serializer.save()
            token=uuid.uuid4()
            Verification(user=user,token=token).save()
            sendMail("Email Verification",f'Dear {user.username} click below link to verify your email\nhttps://rsgtracker.vercel.app/verifyemail/{token}',[user.email])
            # token,created=Token.objects.get_or_create(user=user)
            return Response({"status":True},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class VerificationView(APIView):
    def post(self,r):
        serializer=FCMSerializer(data=r.data)
        if serializer.is_valid():
            try:
                obj=Verification.objects.get(token=serializer.data["token"])
                if obj.is_verified:
                    return Response({"error":"Email already verified"},status=status.HTTP_400_BAD_REQUEST)
                obj.is_verified=True
                obj.save()
                return Response({"status":True},status=status.HTTP_200_OK)
            except:
                return Response({"error":"Invalid link"},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self,r):
        serializer = LoginSerializer(data=r.data)
        if serializer.is_valid():
            try:
                user=User.objects.get(email=serializer.data["email"].lower())
                user=authenticate(username=user.username,password=serializer.data['password'])
                if user is not None:
                    if Verification.objects.filter(user=user,is_verified=True):
                        token,created=Token.objects.get_or_create(user=user)
                        return Response({"token":token.key,"created":created,"status":True},status=status.HTTP_200_OK)
                    else:
                        return  Response({"error":"Email not verified"},status=status.HTTP_400_BAD_REQUEST)
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
class ForgotView(APIView):
    def post(self,r):
        serializer=ForgotSerializer(data=r.data)
        if serializer.is_valid():
            try:
                user=User.objects.get(email=serializer.data["email"])
                ForgotPassword.objects.filter(user=user).delete()
                token=uuid.uuid4()
                sendMail("Password Reset",f"Dear {user.username} click below link to reset password\nhttps://rsgtracker.vercel.app/resetpassword/{token}",[user.email])
                ForgotPassword(user=user,token=token).save()
                return Response({"status":True},status=status.HTTP_200_OK)
            except:
                return Response({"error":"User not found with this email"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
class ResetView(APIView):
    def post(self,r):
        serializer=ResetSerializer(data=r.data)
        if serializer.is_valid():
            if len(serializer.data["password"])<8:
                return Response({"error":"Password must be greater or equal to 8 characters"},status=status.HTTP_400_BAD_REQUEST)
            try:
                if ForgotPassword.objects.filter(token=serializer.data["token"]).exists():
                    obj=ForgotPassword.objects.get(token=serializer.data["token"])
                    if timezone.now()<=obj.expire_date:
                        user=User.objects.get(username=obj.user.username)
                        user.set_password(serializer.data["password"])
                        user.save()
                        obj.delete()
                        sendMail("Password Reset",f"Dear {user.username} your password reset successful",[user.email])
                        return Response({"status":True},status=status.HTTP_200_OK)
                    else:
                        return Response({"error":"Link has been expired"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error":"Invalid link"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error":"Failed to reset password "},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class FCMView(APIView):
    authentication_classes=[TokenAuthentication]
    def post(self,r):
        try:
            serializer=FCMSerializer(data=r.data)
            if serializer.is_valid():
                FCM(token=serializer.data["token"],user=r.auth.user).save()
                return Response({"status":True},status=status.HTTP_200_OK)
        except:
            return Response({"status":False},status=status.HTTP_400_BAD_REQUEST)
        
class AlertView(APIView):
    authentication_classes=[TokenAuthentication]
    def get(self,r):
        serializer=AlertSerializer(Alert.objects.filter(user=r.auth.user),many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,r):
        serializer=AlertSerializer(data=r.data) 
        try:
            if serializer.is_valid():
                if not Alert.objects.filter(slug=serializer.data["slug"],user=r.auth.user).exists():
                    Alert(slug=serializer.data["slug"],name=serializer.data["name"],price=serializer.data["price"],image=serializer.data["image"],user=r.auth.user).save()
                    return Response({"status":True},status=status.HTTP_200_OK)
                else :
                    return Response({"error":"Alert already added"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error":"Failed to add alert"},status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,r,id):
        try:
            Alert.objects.get(id=id).delete()
            return Response({"status":True},status=status.HTTP_200_OK)
        except:
            return Response({"error":"Failed to delete alert"},status=status.HTTP_400_BAD_REQUEST)

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
class DealsView(APIView):
    def get(self,r):
        req=requests.get("https://pricehistoryapp.com/_next/data/7ZxLsuFj5NERQSNdcRvi_/en-IN.json")
        try:
            data=json.loads(req.content)
            return Response(data["pageProps"]["deals"],status=status.HTTP_200_OK)    
        except :
            return Response({"error":"Failed to get results"},status=status.HTTP_400_BAD_REQUEST)
class AddProduct(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,r):
        pass

class ContactView(APIView):
    def post(self,r):
        serializer=ContactSerializer(data=r.data)
        if serializer.is_valid():
            serializer.save()
            sendMail("Form Submit",f'Name:{serializer.data["name"]}\nEmail:{serializer.data["email"]}\nSubject:{serializer.data["subject"]}\nMessage:{serializer.data["message"]}',["rockstarshivaganesh@gmail.com"])
            return Response({"status":True},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
def getPrice(slug):
    try:
        req=requests.get("https://pricehistoryapp.com/product/"+slug)
        soup=bs(req.content,'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        script_content = script.string    
        data = json.loads(script_content)
        data = data.get('props', {}).get('pageProps', {})
        return data["ogProduct"]["price"]
    except:
        return 0
def send_fcm_notification(tokens, title, body,image,link):
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=AAAAhHqY1L0:APA91bF76GAl0BG_JOc9UNOTmQCBAA8irf_7z9zRRIr7NmvM3Gr4VYYTnHAMLb-ZP-td473Bfjek76dYR81a0xnRRFkPihOeTdA8quIotP8uw685M6ZjZJrL-jokGGreuRywtYd7JdJj',  # Replace YOUR_SERVER_KEY with your Firebase Server key
    }
    payload = {
        'registration_ids':tokens ,
        'data': {
            'title': title,
            'body': body,
            'image':image,
            # "icon":"https://rsgmovies.vercel.app/fav_c.png",
            'link':link
        },
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return "Sent "+body
    else:
        return "Failed to sent notification "
class SendFCM(APIView):
    def get(self,r):
        k=[]
        try:
            for i in Alert.objects.all():
                price=getPrice(i.slug)
                if i.price!=price:
                    serializer=FCMSerializer(FCM.objects.filter(user=i.user),many=True)
                    tokens=[j["token"] for j in serializer.data]
                    title=f"Price increased {price}" if price>i.price else f"Price decreased {price}"
                    body=f'The {i.name} Price is {price}'
                    k.append(send_fcm_notification(tokens,title,body,i.image,"/product/"+i.slug))
                    sendMail(title,body+f"\nhttps://rsgtracker.vercel.app/product/{i.slug}",[i.user.email])
                    i.price=price
                    i.save()
            return Response({"status":True,"items":k},status=status.HTTP_200_OK)
        except:
            return Response({"error":"Failed to send notifications"},status=status.HTTP_400_BAD_REQUEST)