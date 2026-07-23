
import razorpay
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from shop.models import Product
from cart.models import Cart,Order_items


# Create your views here.
class AddtoCart(View):
    def get(self,request,i):
        p=Product.objects.get(id=i)
        u=request.user
        try:
            c=Cart.objects.get(user=u,product=p)
            c. quantity+=1
            c.save()
        except:
            c=Cart.objects.create(user=u,product=p,quantity=1)
            c.save()
        return redirect('cart:cartview')
class CartView(View):
    def get(self,request):
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        context={'cart':c,'total':total}
        return render(request, 'cart.html',context)
class CartDecremet(View):
    def get(self,request,i):
        p=Product.objects.get(id=i)
        u=request.user
        try:
            c = Cart.objects.get(user=u, product=p)
            if c.quantity>1:
                c.quantity -= 1
                c.save()
            else:
                c.delete()
        except:
            pass
        return redirect('cart:cartview')
class CartDelete(View):
    def get(self, request, i):
        p = Product.objects.get(id=i)
        u = request.user
        try:
            c = Cart.objects.get(user=u, product=p)
            c.delete()
        except:
            pass
        return redirect('cart:cartview')
from cart.forms import OrderForm
def check_stock(c):
    stock=True
    for i in c:
        if i.product.stock < i.quantity:
            stock=False
            break
    return stock


class Check_Out(View):
    def get(self,request):
        form_instance=OrderForm()
        return render(request,'checkout.html',{'form':form_instance})

    def post(self, request):
        u = request.user
        c = Cart.objects.filter(user=u)
        stock = check_stock(c)
        if stock:
            form_instance = OrderForm(request.POST)

            if form_instance.is_valid():
                # data=form_instance.cleaned_data
                # print(data)
                o=form_instance.save(commit=False)
                o.user=u
                o.save()


                total=0
                for i in c:
                    total+=i.quantity * i.product.price

                for i in c:
                    order=Order_items.objects.create(order=o,product=i.product,quantity=i.quantity)
                    order.save()

                if o.payment_method=="online":
                    # rezopay client connection
                    client=razorpay.Client(auth=( 'rzp_test_RJOSt7QCss7xzs', 'oeSq3Uch497YypT8PW0RTYma'))
                    #replace order
                    response_payment=client.order.create(dict(amount=total*100,currency='INR'))
                    print(response_payment)
                    order_id=response_payment['id']
                    o.order_id=order_id
                    o.amount=total
                    o.save()
                    return render(request,'payment.html',{'payment':response_payment})
                elif o.payment_method=='cod':
                    o.is_ordered=True
                    o.amount=total
                    o.save()

                    items=Order_items.objects.filter(order=o)
                    for i in items:
                        i.product.stock -= i.quantity
                        i.product.save()
                    c.delete()
                    return redirect('shop:categories')

        else:
                messages.error(request,"Currently Items not available")
                print("Items not available")
                return render(request,'payment.html')

    def get(self,request):
        form_instance = OrderForm()
        c=Cart.objects.filter(user=request.user)
        total = 0
        for i in c:
            total += i.quantity * i.product.price
        context={'form':form_instance,'cart':c,'total':total}
        return render(request,'checkout.html',context)
from cart.models import Order
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt,name="dispatch")
class PaymentSuccess(View):
    def post(self,request,i):
        u=User.objects.get(username=i)
        login(request,u)
        response=request.POST #order_id,signature,razor_payment_id
        print(response)
        id=response['razorpay_order_id']
        o=Order.objects.get(order_id=id)
        o.is_ordered=True
        o.save()
        # to reduce the stock
        items = Order_items.objects.filter(order=o)
        for i in items:
            i.product.stock -= i.quantity
            i.product.save()
        #to delete the items from the cart
        c=Cart.objects.filter(user=request.user)
        c.delete()
        return render(request,'payment_success.html')
class YourOrder(View):
    def get(self,request):
        u=request.user
        o=Order.objects.filter(user=u,is_ordered=True)
        context={'order':o}
        return render(request,'yourorder.html',context)

