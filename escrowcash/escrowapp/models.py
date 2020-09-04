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
        ('4de69e374a8ed21cbddd47f2338cc0f479dc58daa2bbe11cd604ca488eca0ddf', 'SPICE Token'),
        ('c4b0d62156b3fa5c8f3436079b5394f7edc1bef5dc1cd2f9d0c4d46f82cca479', 'USDH Token'),
        ('9fc89d6b7d5be2eac0b3787c5b8236bca5de641b5bafafc8f450727b63615c11', 'USDt Token (BCH network)')
    )

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    token = models.CharField(max_length=64, choices=SUPPORTED_TOKEN_CHOICES)
    contract_amount = models.DecimalField(
        max_digits=8, decimal_places=4,
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
    party_released_escrow = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contracts_released', on_delete=models.CASCADE)

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
