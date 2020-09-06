from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('create_contract/<username>/', views.CreateContractOfferView.as_view(), name='create_contract'),
    path('contract_list/', views.ContractListView.as_view(), name='contract_list'),
    path('accept_reject/<pk>/', views.AcceptDeclineContractOfferView.as_view(), name='accept_reject'),
    path('release_contract_fund/<pk>/', views.ReleaseContractFund.as_view(), name='release_contract_fund'),
    path('contract_details/<pk>/', views.ContractDetailView.as_view(), name='contract_details'),
    path('bip70/payment_request/<pk>/', views.generate_payment_request, name='payment_request'),
    path('bip70/handle_payment/<pk>/', views.handle_payment, name='handle_payment'),
]
