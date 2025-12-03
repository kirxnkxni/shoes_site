from django.shortcuts import render,redirect
from.models import *
from django.core.mail import send_mail
from django.conf import settings
import random
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def header(req):
    return render(req,'header.html')

def home(req):
    result=Product.objects.all()
    return render(req,'home.html',{'result':result})

def footer(req):
    return render(req,'footer.html')

def get_data(req):
    result=Product.objects.all()
    return render(req,'home.html',{'result':result})

def contact(req):
    return render(req,'contact.html')

# =======================================login==============================================================================

def login(req):
    if req.method == 'POST':
        try:
            email=req.POST.get('username')
            entered_pass=req.POST.get('password')
            remember=req.POST.get('remember')

            if not email or not entered_pass:
                return JsonResponse({'status':"fill",'message':'please fill the fields'})

            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist: 
                return JsonResponse({'status':"nouser",'message':'invalid user!'})
            
            if not check_password(entered_pass,user_obj.password):
                return JsonResponse({'status':"invalid",'message':"invalid username or password"})
            
            req.session['user_id']=user_obj.id

            if remember:
                req.session.set_expiry(60 * 60 * 24 * 15)
            else:
                req.session.set_expiry(0)

            return JsonResponse({'status':"success",'message':'login successful'})

        except Exception as e:
            print("LOGIN ERROR:", e)
            return JsonResponse({'status': "error", 'message': 'Something went wrong!'})            
    
    return render(req,'login.html')

# ==================================== forgot forgot_password ================================================ #

def otp_generate():
    return str(random.randint(100000,999999))

def forgot_password(req):

    if req.method=='POST':
        email=req.POST.get("email")
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'message':'email not registered'})
        
        otp=otp_generate()
        EmailOtp.objects.create(email=email,otp=otp)
        req.session["reset_email"]=email

        style_otp=f"""
                    <p style="font-size: larger; display: flex; justify-content: center;">your otp for resetting password is</p>
                    <p style="font-size: xx-large; font-weight: bold; display: flex; justify-content: center;">{ otp }</p>
                    <p style="font-size: larger; display: flex; justify-content: center;">expires in 5 minutes</p>
                    """
                    
        send_mail(
            subject="OTP FOR PASSWORD RESETTING",
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=style_otp,
            fail_silently=False
        )
        return JsonResponse({'message':'otp sent successfully'})
    
    return render(req,'forgot_password.html')


# ================================================password resetting===========================================================

def verify_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get("entered_otp")
        email = request.session.get("reset_email")

        otp_obj = EmailOtp.objects.filter(email=email).order_by("-created_time").first()

        if not email:
            return JsonResponse({'message':'session expired'})

        if not otp_entered:
            return JsonResponse({"message": "Please enter OTP"})

        if otp_obj and otp_entered == otp_obj.otp:
            return JsonResponse({"message": "OTP verified!"})
        else:
            return JsonResponse({"message": "Invalid OTP!"})
        
    return JsonResponse({"message": "Invalid request method"})

        
def change_password(req):
    if req.method=="POST":
        new_pass=req.POST.get("newpassword")
        conf_pass=req.POST.get("confirmpassword")
        email=req.session.get("reset_email")

        if not new_pass or not conf_pass:
            return JsonResponse({'message':'please fill the fields'})
        
        if new_pass != conf_pass:
            return JsonResponse({'message':'password do not match'})
        
        if len(new_pass)<6 :
            return JsonResponse({'message':'password must be atleast 6 character'})
        
        try:
            user_obj=User.objects.get(email=email)
            user_obj.password=make_password(new_pass)
            user_obj.save()
            req.session.pop('reset_email',None)
            return JsonResponse({'message':'password changed successfully'})
        except User.DoesNotExist:
            return JsonResponse({'message':"user not found!"})

def reset(req):
    return render(req,'reset.html')

def signup(req):
    return render(req,'signup.html')

def cart(req):
    return render(req,'cart.html')

def checkout(req):
    return render(req,'checkout.html')

def order_summary(req):
    return render(req,'order_summary.html')

def profile(req):
    return render(req,'profile.html')

def product_details(req):
    return render(req,'product_details.html')