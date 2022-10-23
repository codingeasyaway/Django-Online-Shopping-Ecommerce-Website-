from urllib import request

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, FormView, DeleteView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout

from .forms import CheckoutForm, CustomerRegistrationForm, CustomerLoginForm
from .models import *
from django.db.models import Q
from django.core.paginator import Paginator
# Create your views here.


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)

# Home
class HomeView(TemplateView):
    template_name = 'ecommerce/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list

        context['category'] = Category.objects.all()

        return context

# All Product
class AllProductView(EcomMixin, TemplateView):
    template_name = 'ecommerce/allproduct.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all().order_by("-id")
        return context

# Details Product
class ProductDetailView(EcomMixin, TemplateView):
    template_name = 'ecommerce/detailsproducts.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context

# Add to Cart
class AddToCartView(EcomMixin, TemplateView):
    template_name = 'ecommerce/addtocart.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get id from requested url
        product_id = kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)
        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            #items already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price,
                                                     quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()
        # check if product already exists in cart
        return context

# My Cart
class MyCartView(EcomMixin, TemplateView):
    template_name = 'ecommerce/mycart.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)

        else:
            cart = None
        context['cart'] = cart
        return context

# Manage Cart
class ManageCartView(EcomMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        cp_id = kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "drc":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("eapp:MyCart")

# Empty Cart
class EmptyCartView(EcomMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("eapp:MyCart")

# Check Out
class CheckoutView(EcomMixin, CreateView):
    template_name = "ecommerce/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("eapp:Home")
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_id = None
        context['cart'] = cart_obj
        return context
    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status ="Order Received"
            del self.request.session['cart_id']

        else:
            return redirect("eapp:Home")
        return super().form_valid(form)

# About
class AboutView(EcomMixin, TemplateView):
    template_name = 'ecommerce/about.html'

# contact
class ContactView(EcomMixin, TemplateView):
    template_name = 'ecommerce/contact.html'

# Customer Registration
class CustomerRegistrationVeiw(CreateView):
    template_name = 'ecommerce/Registration.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("eapp:Home")
    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

# login
class LoginView(FormView):
    template_name = 'ecommerce/login.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy("eapp:Home")
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        upass = form.cleaned_data.get("password")
        auth_users = authenticate(username=uname, password=upass)
        if auth_users is not None and Customer.objects.filter(user=auth_users).exists():
            login(self.request, auth_users)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': "Invalid username or password! please try again."})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

# logout
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("eapp:Home")


# User Profile
class ProfileView(EcomMixin, TemplateView):
    template_name = 'ecommerce/profile.html'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer =self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders'] = orders
        return context

class CustomerOrderDetailsView(DeleteView):
    template_name = 'ecommerce/customerorderdetails.html'
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            order_id =self.kwargs["pk"]
            order = Order.objects.get(id=order_id)

            if request.user.customer != order.cart.customer:
                return redirect("/profile/")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

# Search
class SearchView(TemplateView):
    template_name = "ecommerce/search.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET["keyword"]
        results = Product.objects.filter(Q(title__icontains=kw))
        context["results"] = results
        return context


# admin login page

class AdminLoginView(FormView):
    template_name = "admindashboard/login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy('eapp:AdminHome')
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        upass = form.cleaned_data.get("password")
        auth_users = authenticate(username=uname, password=upass)
        if auth_users is not None and Admin.objects.filter(user=auth_users).exists():
            login(self.request, auth_users)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': "Invalid username or password! please try again."})
        return super().form_valid(form)

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")

#Admin home page
class AdminHomeView(TemplateView, AdminRequiredMixin):
    template_name = "admindashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorder"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context


# Admin Order Details
class AdminOrderDetails(DetailView, AdminRequiredMixin):
    template_name = "admindashboard/adminorderdetails.html"
    model = Order
    context_object_name = "ord_obj"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context


# Admin Order list
class AdminOrderlist(ListView, AdminRequiredMixin):
    template_name = "admindashboard/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"



# Admin Order Status
class AdminOrderStatusChange(View, AdminRequiredMixin):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("eapp:AdminOrderDetails", kwargs={"pk": order_id}))


