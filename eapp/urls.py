from django.urls import path
from .views import *

app_name= 'eapp'
urlpatterns = [
    path('', HomeView.as_view(), name= 'Home'),
    path('about/', AboutView.as_view(), name='About'),
    path('contact/', ContactView.as_view(), name='Contact'),
    path('all-product/', AllProductView.as_view(), name='AllProducts'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='ProductDetail'),
    path('add-to-cart/<int:pro_id>/', AddToCartView.as_view(), name='AddToCart'),
    path('my-cart/', MyCartView.as_view(), name='MyCart'),
    path('manage-cart/<int:cp_id>/', ManageCartView.as_view(), name='ManageCart'),
    path('empty-cart/', EmptyCartView.as_view(), name='EmptyCart'),
    path('checkout/', CheckoutView.as_view(), name='Checkout'),
    path('register/', CustomerRegistrationVeiw.as_view(), name='CustomerRegistration'),
    path('login/', LoginView.as_view(), name='CustomerRegistration'),
    path('logout/', LogoutView.as_view(), name='Logout'),
    path('profile/', ProfileView.as_view(), name='Profile'),
    path('profile/order-<int:pk>/', CustomerOrderDetailsView.as_view(), name='customerorderdetails'),
    path('search/', SearchView.as_view(), name='Search'),

    # admin site pages
    path('admin-login/', AdminLoginView.as_view(), name='AdminLogin'),
    path('admin-home/', AdminHomeView.as_view(), name='AdminHome'),
    path('admin-order-details/<int:pk>', AdminOrderDetails.as_view(), name='AdminOrderDetails'),
    path('admin-all-order/', AdminOrderlist.as_view(), name='AdminOrderList'),
    path('admin-order-<int:pk>-change/', AdminOrderStatusChange.as_view(), name='AdminOrderStatusChange'),
]