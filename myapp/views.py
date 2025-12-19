from django.shortcuts import render,redirect
from.models import *
from django.core.mail import send_mail
from django.conf import settings
import random
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone
from datetime import timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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

# =======================================================signup===================================================================

def signup(req):
    if req.method == 'POST':
       first_name=req.POST.get('firstname')
       last_name=req.POST.get('lastname')
       email=req.POST.get('usermail')
       password=req.POST.get('password')
       confirm_password=req.POST.get('confirmpass')

       if not first_name or not last_name or not email or not password or not confirm_password:
            return JsonResponse({'status':'fill','message':'please fill the fields'})
       
       user_name=first_name + " " + last_name

       try:
            validate_email(email)
       except ValidationError:
            return JsonResponse({'status':'email_valid','message':'enter a valid email'})
       
       if User.objects.filter(email=email).exists():
            return JsonResponse({'status':'user_exist','message':'user already exists'})
       
       if password != confirm_password:
            return JsonResponse({'status':'invalid_pass','message':'passwords do not match'})
       else:
            save_pass=make_password(password)

       User.objects.create(
            user=user_name,
            email=email,
            password=save_pass,
        )
       return JsonResponse({'status':'success','message':'sign-up successful'})
    return render(req,'signup.html')


# =============================================profile=============================================================

def profile(req):
    # Check if user is logged in
    user_id = req.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    # Get user
    user = User.objects.get(id=user_id)
    
    # Get or create profile
    profile_obj, created = Profile.objects.get_or_create(user=user)
    
    return render(req, 'profile.html', {
        'user': user,
        'profile': profile_obj
    })


#===================================logout=============================================

def logout(req):
    req.session.flush()  # Clear all session data
    return redirect('login')

#===========================================================edit_profile===============================================================

def edit_profile(req):
    # Check if user is logged in
    user_id = req.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    profile_obj, created = Profile.objects.get_or_create(user=user)
    
    if req.method == 'POST':
        try:
            # Get form data
            full_name = req.POST.get('fullname')
            gender = req.POST.get('gender')
            age = req.POST.get('age')
            phone = req.POST.get('phone')
            address = req.POST.get('address')
            profile_image = req.FILES.get('profile_image')
            
            # Update user name
            if full_name:
                user.user = full_name
                user.save()
            
            # Update profile
            if gender:
                profile_obj.gender = gender
            if age:
                profile_obj.age = age
            if phone:
                profile_obj.phone = phone
            if address:
                profile_obj.address = address
            if profile_image:
                profile_obj.image = profile_image
            
            profile_obj.save()
            
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(req, 'edit_profile.html', {
        'user': user,
        'profile': profile_obj
    })

#===================================================================add account====================================================

def add_account(req):
    # Get current user if logged in
    current_user_id = req.session.get('user_id')
    current_user = None
    if current_user_id:
        current_user = User.objects.get(id=current_user_id)
    
    # Get all users for account switching (you might want to limit this to users who've logged in on this device)
    all_users = User.objects.all()
    
    return render(req, 'add_account.html', {
        'current_user': current_user,
        'all_users': all_users
    })

def switch_account(req, user_id):
    # Switch to different account
    req.session['user_id'] = user_id
    return redirect('profile')

# =====================================cart=====================================================

def add_to_cart(req, product_id):
    if req.method == 'POST':
        # Check if user is logged in
        user_id = req.session.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Please login first'})
        
        try:
            user = User.objects.get(id=user_id)
            product = Product.objects.get(id=product_id)
            
            # Check if item already in cart
            cart_item = Cart.objects.filter(customer=user, Product=product).first()
            
            if cart_item:
                # Item exists, increase quantity
                cart_item.qty += 1
                cart_item.save()
                message = 'Quantity updated in cart'
            else:
                # New item, create cart entry
                Cart.objects.create(customer=user, Product=product, qty=1)
                message = 'Added to cart'
            
            # Get total cart count
            cart_count = Cart.objects.filter(customer=user).count()
            
            return JsonResponse({
                'status': 'success', 
                'message': message,
                'cart_count': cart_count
            })
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def cart(req):
    # Check if user is logged in
    user_id = req.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    cart_items = Cart.objects.filter(customer=user).select_related('Product')
    
    # Calculate totals
    subtotal = sum(float(item.Product.price) * item.qty for item in cart_items)
    shipping = 50.00 if subtotal > 0 else 0  # Flat shipping rate
    tax = subtotal * 0.05  # 5% tax
    total = subtotal + shipping + tax
    
    return render(req, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'item_count': cart_items.count()
    })


def update_cart_quantity(req):
    if req.method == 'POST':
        user_id = req.session.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Please login first'})
        
        try:
            cart_id = req.POST.get('cart_id')
            action = req.POST.get('action')  # 'increase' or 'decrease'
            
            cart_item = Cart.objects.get(id=cart_id)
            
            if action == 'increase':
                cart_item.qty += 1
                cart_item.save()
            elif action == 'decrease':
                if cart_item.qty > 1:
                    cart_item.qty -= 1
                    cart_item.save()
                else:
                    # If quantity is 1 and user clicks decrease, remove item
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'removed',
                        'message': 'Item removed from cart'
                    })
            
            # Calculate new item total
            item_total = float(cart_item.Product.price) * cart_item.qty
            
            # Calculate new cart totals
            user = User.objects.get(id=user_id)
            cart_items = Cart.objects.filter(customer=user)
            subtotal = sum(float(item.Product.price) * item.qty for item in cart_items)
            shipping = 50.00 if subtotal > 0 else 0
            tax = subtotal * 0.05
            total = subtotal + shipping + tax
            
            return JsonResponse({
                'status': 'success',
                'qty': cart_item.qty,
                'item_total': round(item_total, 2),
                'subtotal': round(subtotal, 2),
                'shipping': round(shipping, 2),
                'tax': round(tax, 2),
                'total': round(total, 2)
            })
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def remove_from_cart(req):
    if req.method == 'POST':
        user_id = req.session.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'Please login first'})
        
        try:
            cart_id = req.POST.get('cart_id')
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.delete()
            
            # Calculate new cart totals
            user = User.objects.get(id=user_id)
            cart_items = Cart.objects.filter(customer=user)
            subtotal = sum(float(item.Product.price) * item.qty for item in cart_items)
            shipping = 50.00 if subtotal > 0 else 0
            tax = subtotal * 0.05
            total = subtotal + shipping + tax
            
            return JsonResponse({
                'status': 'success',
                'message': 'Item removed from cart',
                'subtotal': round(subtotal, 2),
                'shipping': round(shipping, 2),
                'tax': round(tax, 2),
                'total': round(total, 2),
                'item_count': cart_items.count()
            })
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

#==============================================================checkout========================================================#

def checkout(req):
    return render(req,'checkout.html')

def order_summary(req):
    return render(req,'order_summary.html')


def product_details(req):
    return render(req,'product_details.html')


def shop(req):
    result=Product.objects.all()
    return render(req,'shop.html',{'result':result})