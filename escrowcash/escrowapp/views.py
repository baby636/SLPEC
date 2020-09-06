import time
import requests

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth import get_user_model
from django import forms
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Contract
from . import bip70_pb2

User = get_user_model()
# Create your views here.


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class ContractListView(generic.ListView):
    model = Contract
    template_name = 'escrowapp/contract_list.html'


@method_decorator(login_required, name='dispatch')
class ContractDetailView(generic.DetailView):
    model = Contract
    template_name = 'escrowapp/contract_details.html'


@method_decorator(login_required, name='dispatch')
class ReleaseContractFund(generic.UpdateView):
    model = Contract
    fields = ()
    template_name = 'escrowapp/release_contract_fund.html'
    success_url = reverse_lazy('contract_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        releaser = self.request.user
        if releaser == self.object.party_making_offer:
            user_who_gets_fund = self.object.party_taking_offer
        # charge back!
        if releaser == self.object.party_taking_offer:
            user_who_gets_fund = self.object.party_making_offer

        self.object.release_contract_fund(self, user_who_gets_fund, releaser)
        return HttpResponseRedirect(
            reverse_lazy('contract_details', kwargs={'pk': self.object.pk})
        )


@csrf_exempt
def generate_payment_request(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    url = settings.SMART_CONTRACT_SERVER_URL + '/api/create_op_return_outputs'
    result = requests.post(
        url=url,
        data={
            'address': contract.contract_cash_address,
            'token': contract.token,
            'amount': int(contract.contract_amount * 10 ** 8)
        }
    )
    assert result.status_code == 200
    output_data = result.json()
    out_script_hex_list = [
        output_data['op_return'],
        output_data['contract_output'],
        output_data['fee_output']
    ]

    outputs = list()
    amount = 0
    for output in out_script_hex_list:
        outputs.append(
            bip70_pb2.Output(
                script=bytes.fromhex(output),
                amount=amount
            )
        )
        # change to dust amount after non op return data
        if amount == 0:
            amount = 546

    payment_details = bip70_pb2.PaymentDetails(
        outputs=outputs,
        time=int(time.time()),
        expires=int(time.time() + 2000000),
        merchant_data=b'',
        memo='FREEDOM!',
        payment_url=request.build_absolute_uri(reverse('handle_payment', kwargs={'pk': pk})),
    )
    payment_request = bip70_pb2.PaymentRequest(
        serialized_payment_details=payment_details.SerializeToString()
    )
    serialized_payment_request = payment_request.SerializeToString()
    # url = settings.SMART_CONTRACT_SERVER_URL + '/api/sign_payment_request'
    # result = requests.post(
    #     url=url,
    #     data={'payment_request': serialized_payment_request.hex()}
    # )
    #
    # print(bytes.fromhex(result.json()['payment_request']))
    # return HttpResponse(
    #     bytes.fromhex(result.json()['payment_request']),
    #     content_type='application/simpleledger-paymentrequest',
    # )
    return HttpResponse(
        payment_request.SerializeToString(),
        content_type='application/simpleledger-paymentrequest',
    )

@csrf_exempt
def handle_payment(request, pk):
    contract = get_object_or_404(Contract, pk=pk, state='accepted')

    if request.method == 'POST':
        payment = bip70_pb2.Payment()
        payment.ParseFromString(request.body)
        transaction_hex = payment.transactions[0].hex()

        # broadcast the transaction
        # TODO: do validation
        url = settings.BCH_REST_API_BASE_URL +\
            '/rawtransactions/sendRawTransaction/' + transaction_hex
        result = requests.get(url)
        if not result.status_code == 200:
            print(result.text)
        print("contract funded:", contract.fund_contract())

        payment_ack = bip70_pb2.PaymentACK(payment=payment)
        return HttpResponse(
            payment_ack.SerializeToString(),
            content_type='application/simpleledger-paymentrequest',
        )
