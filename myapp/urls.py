from .import views
from django.urls import path

urlpatterns = [
    path('header/',views.header, name='header'),
    path('home/',views.home, name='home'),
    path('footer/',views.footer, name='footer'),
    path('get_data/',views.get_data,name='get_data'),
    path('contact/',views.contact,name='contact'),
    path('login/',views.login,name='login'),
    path('forgot/',views.forgot_password,name='forgot'),
    path('reset/',views.reset,name='reset'),
    path('otp_verify',views.verify_otp,name='verify_otp'),
    path('change_password/',views.change_password,name='change_password'),
    path('signup/',views.signup,name='signup'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('order_summary/',views.order_summary,name='order_summary'),
    path('profile/',views.profile,name='profile'),
    path('product_details/',views.product_details,name='prod_details')
] 