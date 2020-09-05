# Generated by Django 3.1.1 on 2020-09-04 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escrowapp', '0002_auto_20200904_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='arbitrator_pub_key',
            field=models.CharField(default='', max_length=67),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_cash_address',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='party_making_offer_encrypted_priv_key',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='party_making_offer_pub_key',
            field=models.CharField(default='', max_length=67),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='party_taking_offer_encrypted_priv_key',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='party_taking_offer_pub_key',
            field=models.CharField(blank=True, max_length=67, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='signature',
            field=models.TextField(blank=True, null=True),
        ),
    ]