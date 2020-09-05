from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth import get_user_model
from django import forms
from django.urls import reverse_lazy

from .models import Contract
User = get_user_model()
# Create your views here.


class CreateContractOfferView(generic.CreateView):
    model = Contract
    fields = (
        'party_making_offer_pub_key',
        'party_making_offer_encrypted_priv_key',
        'token',
        'contract_amount',
        'contract_terms',
    )

    def dispatch(self, request, *args, **kwargs):
        username = kwargs['username']
        get_object_or_404(User, username=username)
        return super().dispatch(request, *args, *kwargs)

    def get_context_data(self, **kwargs):
        print(self.kwargs)
        context_data = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        context_data['user'] = user
        return context_data

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['party_making_offer_pub_key'].widget = forms.HiddenInput()
        form.fields['party_making_offer_encrypted_priv_key'].widget = forms.HiddenInput()
        return form

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        form_kwargs['instance'] = Contract()
        form_kwargs['instance'].party_making_offer = self.request.user

        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        form_kwargs['instance'].party_taking_offer = user

        return form_kwargs

    template_name = 'escrowapp/create_contract_offer.html'
    success_url = reverse_lazy('contract_list')


class AcceptDeclineContractOfferView(generic.UpdateView):
    model = Contract
    fields = (
        'offer_accepted',
        'party_taking_offer_pub_key',
        'party_taking_offer_encrypted_priv_key'
    )
    template_name = 'escrowapp/update_contract_offer.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['party_taking_offer_pub_key'].widget = forms.HiddenInput()
        form.fields['party_taking_offer_encrypted_priv_key'].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.accept_and_build_escrow_smart_contract()
        return HttpResponseRedirect(reverse_lazy('contract_details', kwargs={'pk': self.object.pk}))


class ContractListView(generic.ListView):
    model = Contract
    template_name = 'escrowapp/contract_list.html'


class ContractDetailView(generic.DetailView):
    model = Contract
    template_name = 'escrowapp/contract_details.html'
