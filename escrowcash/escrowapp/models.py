from django.db import models
from django.conf import settings
# Create your models here.


class Contract(models.Model):
    CONTRACT_STATES = (
        ("offer", "Offer"),
        ("offer_denied", "Offer Denied"),
        ("contract_funded", "Contract Funded"),
        ("released", "Released"),
        ("dispute", "Dispute"),
        ("released_by_arbitrator", "Released By Arbitrator")
    )

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    state = models.CharField(max_length=23, choices=CONTRACT_STATES, default=CONTRACT_STATES[0][0])
    offer_accepted = models.BooleanField(null=True, blank=True)

    party_making_offer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contracts_made', on_delete=models.CASCADE)
    party_taking_offer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contracts_accepted', on_delete=models.CASCADE)
    party_released_escrow = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contracts_released', on_delete=models.CASCADE)