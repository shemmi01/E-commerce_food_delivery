from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from pizza.models import *
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required

# Create your views here.
from instamojo_wrapper import Instamojo
from django.conf import settings

api = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')




def home(request):
    pizzas = Pizza.objects.all()
    context= {'pizzas': pizzas}
    print(context)
    return render(request,  'home.html', context)

def login_page(request):
   

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

           # if user is not exist then show message not found and rend it to login
            user_obj = User.objects.filter(username= username)
            if not user_obj.exists():
                messages.warning(request, 'User not found')
                return redirect('/login/')

            #auth checks pwd and uname 
            user_obj = authenticate(username= username, password = password)
            #if it is there then login
            if user_obj:
                login(request, user_obj)
                return redirect('/')
            #otherwise if that particular user is not exist written wrong pwd
            messages.error(request, 'Wrong password')
            return redirect('/login/')

        except Exception as e:
            messages.error(request, 'something went wrong')
            return redirect('/register/')
    return render(request,'login.html')


def register_page(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            #if user already exist send them as username taken already
            user_obj = User.objects.filter(username = username)
            if user_obj.exists():
                messages.error(request, 'Username is taken.')
                return redirect('/register/')
            
            #if user is not exist
            user_obj = User.objects.create(username = username)
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, 'Your account has been created.')
            return redirect('/login/')
            
        except Exception as e:
            messages.error(request, 'something went wrong.')
            return redirect('/register/')   
    return render(request, 'register.html')
       

@login_required(login_url='/login/')
def add_cart(request,pizza_uid):
    user = request.user
    pizza_obj = Pizza.objects.get(uid = pizza_uid)
    cart , _ = Cart.objects.get_or_create(user = user, is_paid =False)

    #add on cart item
    cart_items = CartItems.objects.create(
        cart = cart, 
        pizza = pizza_obj
    )
    return redirect("/")

from django.conf import settings
@login_required(login_url='/login/')

def cart(request):
    cart =Cart.objects.get(is_paid = False, user = request.user)
   
    response = api.payment_request_create(amount = cart.get_cart_total(),
        purpose = 'Order',
        buyer_name = request.user.username,
        redirect_url ="http://127.0.0.1:8000/success"
        
    )
    cart.instamojo_id = response['payment_request']['id']
    cart.save()

    context = {'carts' : cart, 'payment_url': response['payment_request']['longurl']}
    print(response)

    return render(request, 'cart.html', context)




@login_required(login_url='/login/')
def remove_cart_items(request, cart_item_uid):
    try:
        CartItems.objects.get(uid = cart_item_uid).delete()
        return redirect('/cart/') 
    except Exception as e:
        print(e)
@login_required(login_url='/login/')
def orders(request):
    orders = Cart.objects.filter(is_paid = True ,user= request.user)
    context = {'orders': orders}
    return render(request,'orders.html',context)
@login_required (login_url='/login/')     
def payment(request):
    return render(request , 'payment.html')
@login_required(login_url='/login/') 
def success(request):
        payment_request = request.GET.get("payment_request_id")
        cart= Cart.objects.get(instamojo_id =payment_request )
        cart.is_paid = True
        cart.save()
        return redirect('/orders/')
    
    
