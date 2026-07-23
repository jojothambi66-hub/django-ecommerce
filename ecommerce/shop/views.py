from django.shortcuts import render,redirect
from django.views import View
from shop.models import Category
# Create your views here.
class AdminHome(View):
    def get(self,request):
        return render(request,'adminhome.html')
class CategoryView(View):
    def get(self,request):
        c=Category.objects.all()
        context={'category':c}
        return render(request,'categories.html',context)
class ProductView(View):
    def get(self,request,i):
        b = Category.objects.get(id=i)
        context={'category':b}
        return render(request,'product.html',context)
from shop.models import Product
class ProductDetail(View):
    def get(self,request,i):
        b=Product.objects.get(id=i)
        context={'products':b}
        return render(request,'productdetail.html',context)
from shop.forms import SignupForm,LoginForm
class Register(View):
    def get(self,request):
        form_instance=SignupForm()
        context={'form':form_instance}
        return render(request,'register.html',context)
    def post(self,request):
        form_instance=SignupForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:userlogin')
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
class Userlogin(View):
    def post(self,request):
        form_instance = LoginForm(request.POST)
        if form_instance.is_valid():
            name=form_instance.cleaned_data['username']
            pwd=form_instance.cleaned_data['password']
            user=authenticate(username=name,password=pwd)
            if user and user.is_superuser==True :
                login(request,user)
                return redirect('shop:admin')
            elif user and user.is_superuser != True:
                login(request, user)
                return redirect('shop:categories')

            else:
                messages.error(request,"Invalid Credentails,Please enter valid Username and Password")
                return render(request, 'login.html',{'form': form_instance})

    def get(self, request):
        form_instance = LoginForm()
        context = {'form': form_instance}
        return render(request,'login.html',context)
class Userlogout(View):
    def get(self,request):
        logout(request)
        return redirect('shop:categories')
from shop.forms import CategoryForm, ProductForm, StockForm
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
class AddCategeory(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self,request):
        form_instance =  CategoryForm()
        context = {'form': form_instance}
        return render(request, 'addcategory.html', context)
    def post(self,request):
        form_instance = CategoryForm(request.POST,request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')

class AddProduct(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return self.request.user.is_superuser
    def get(self,request):
        form_instance = ProductForm()
        context = {'form': form_instance}
        return render(request, 'addproduct.html', context)
    def post(self,request):
        form_instance = ProductForm(request.POST,request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')
class AddStock(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return self.request.user.is_superuser
    def get(self,request,i):
        p=Product.objects.get(id=i)
        form_instance = StockForm(instance=p)
        context = {'form': form_instance}
        return render(request,'addstock.html',context)

    def post(self, request,i):
        p = Product.objects.get(id=i)
        form_instance = StockForm(request.POST,instance=p)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')
from django.db.models import Q
class SearchView(View):
    def post(self,request):
        query = request.POST['q']
        b = Product.objects.filter(Q(name__icontains=query) | Q(price__icontains=query))
        context = {'searches': b}
        return render(request, 'search.html', context)

