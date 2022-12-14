# Generated by Django 3.1.1 on 2020-09-06 11:12

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escrowapp', '0006_auto_20200905_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='contract_amount',
            field=models.DecimalField(decimal_places=8, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('10.0'))]),
        ),
        migrations.AlterField(
            model_name='contract',
            name='token',
            field=models.CharField(choices=[('21b7074cb38d5b6ceba82cc8af4e61c16399529fc5d93d43e3fdc5aa21e8fa08', 'USDf (USD Fake) Token'), ('4de69e374a8ed21cbddd47f2338cc0f479dc58daa2bbe11cd604ca488eca0ddf', 'SPICE Token'), ('c4b0d62156b3fa5c8f3436079b5394f7edc1bef5dc1cd2f9d0c4d46f82cca479', 'USDH Token'), ('9fc89d6b7d5be2eac0b3787c5b8236bca5de641b5bafafc8f450727b63615c11', 'USDt Token (BCH network)')], max_length=64),
        ),
    ]
