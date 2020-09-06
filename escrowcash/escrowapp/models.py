import requests
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
# Create your models here.


class Contract(models.Model):
    CONTRACT_STATES = (
        ("offer", "Offer"),
        ("accepted", "Accepted"),
        ("offer_declined", "Offer Declined"),
        ("contract_funded", "Contract Funded"),
        ("released", "Released"),
        ("dispute", "Dispute"),
        ("released_by_arbitrator", "Released By Arbitrator")
    )

    SUPPORTED_TOKEN_CHOICES = (
        ('21b7074cb38d5b6ceba82cc8af4e61c16399529fc5d93d43e3fdc5aa21e8fa08', 'USDf (USD Fake) Token'),
        ('4de69e374a8ed21cbddd47f2338cc0f479dc58daa2bbe11cd604ca488eca0ddf', 'SPICE Token'),
        ('c4b0d62156b3fa5c8f3436079b5394f7edc1bef5dc1cd2f9d0c4d46f82cca479', 'USDH Token'),
        ('9fc89d6b7d5be2eac0b3787c5b8236bca5de641b5bafafc8f450727b63615c11', 'USDt Token (BCH network)')
    )

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    token = models.CharField(max_length=64, choices=SUPPORTED_TOKEN_CHOICES)
    contract_amount = models.DecimalField(
        max_digits=12, decimal_places=8,
        validators=[MinValueValidator(Decimal("10.0"))]
    )
    contract_terms = models.TextField()
    state = models.CharField(max_length=23, choices=CONTRACT_STATES, default=CONTRACT_STATES[0][0])
    offer_accepted = models.BooleanField(null=True, blank=True)

    arbitrator_pub_key = models.CharField(max_length=67)
    party_making_offer_pub_key = models.CharField(max_length=67)
    party_making_offer_encrypted_priv_key = models.TextField()
    party_taking_offer_pub_key = models.CharField(max_length=67, null=True, blank=True)
    party_taking_offer_encrypted_priv_key = models.TextField(null=True, blank=True)

    contract_cash_address = models.CharField(max_length=55, blank=True, null=True)
    signature = models.TextField(blank=True, null=True)

    party_making_offer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contracts_made', on_delete=models.CASCADE)
    party_taking_offer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contracts_accepted', on_delete=models.CASCADE)
    party_released_escrow = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contracts_released',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    party_contract_released_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contracts_released_to',
        on_delete=models.CASCADE,
        blank=True, null=True
    )

    def accept_and_build_escrow_smart_contract(self):
        url = settings.SMART_CONTRACT_SERVER_URL + '/api/build_escrow_contract'
        result = requests.post(
            url=url,
            data={
                'party_making_offer_pub_key': self.party_making_offer_pub_key,
                'party_taking_offer_pub_key': self.party_taking_offer_pub_key
            }
        )
        assert result.status_code == 200
        data = result.json()
        self.contract_cash_address = data['address']
        self.offer_accepted = True
        self.state = self.CONTRACT_STATES[1][0]  # accepted
        self.save()

    def decline(self):
        self.offer_accepted = False
        self.state = self.CONTRACT_STATES[2][0]  # offer_declined
        self.save()

    def fund_contract(self):
        url = settings.BCH_REST_API_BASE_URL +\
              '/slp/balancesForAddress/' + self.contract_cash_address
        contract_address_balance_http_result = requests.get(url=url)
        assert contract_address_balance_http_result.status_code == 200
        contract_address_balance = contract_address_balance_http_result.json()
        for row in contract_address_balance:
            if row['tokenId'] == self.token:
                address_balance = row['balance'] * 10 ** row['decimalCount']
                print('address balance:', address_balance)
                if row['balance'] * 10 ** row['decimalCount'] >= self.contract_amount * 100000000:  # 100000000 because of 4 decimal places of contract_amount
                    self.state = self.CONTRACT_STATES[3][0]
                    self.save()
                    return True
        return False

    def release_contract_fund(self, user_who_gets_fund, releaser=None):
        if user_who_gets_fund == self.party_making_offer:
            message = 'PartyOneTakes'
        else:
            message = 'partyTwoTakes'
        url = settings.SMART_CONTRACT_SERVER_URL + '/api/release_contract'
        result = requests.post(url=url, data={'message': message})
        assert result.status_code == 200
        data = result.json()

        self.signature = data['signature']
        self.arbitrator_pub_key = data['arbitrator_pub_key']
        self.party_released_escrow = releaser
        self.party_contract_released_to = user_who_gets_fund
        self.state = self.CONTRACT_STATES[4][0]
        self.save()
