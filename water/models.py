from django.db.models import PROTECT # type: ignore
from django.db import models # type: ignore
from django.db.models import Q  # type: ignore # This imports Q for complex queries


# ========================  MODELS  ========================
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    street_no = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    email = models.EmailField(unique=True)  # Ensure email is unique
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'Customers'  # Specify the existing table name

    def __str__(self):
        return self.family_name  # Display family name in dropdown

class Place(models.Model):
    place_id = models.AutoField(primary_key=True)
    place_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    street_no = models.CharField(max_length=10)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.place_name    

    class Meta:
        db_table = 'Places'


class Watermeter(models.Model):
    watermeter_id = models.AutoField(primary_key=True)
    sn = models.CharField(max_length=100, unique=True)  # Serial number must be unique
    mbus_adr = models.CharField(max_length=100, unique=True)  # MBus address must be unique
    recent_reading = models.FloatField(blank=True, null=True)
    date_of_recent_reading = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"SN: {self.sn} - MBus: {self.mbus_adr}"

    class Meta:
        db_table = 'Watermeters'  # Specify the existing table name


class WatermetersPlaces(models.Model):
    watermeters_places_id = models.AutoField(primary_key=True)    
    watermeter = models.OneToOneField(Watermeter, on_delete=models.CASCADE)  # One-to-One relationship
    place = models.OneToOneField(Place, on_delete=models.CASCADE)            
    
    class Meta:
        db_table = 'Watermeters_Places'  # Specify the existing table name
        unique_together = (('watermeter', 'place'),)  # Ensure the Watermeter-Place combination is unique

    def __str__(self):
        return str(self.place)  # Display place name in dropdown


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    
    # Use PROTECT for both customer and watermeters_places to prevent deletion if they are connected to a contract
    customer = models.ForeignKey(Customer, on_delete=PROTECT)  # Prevent deletion of a customer if it's connected to a contract
    watermeters_places = models.ForeignKey(WatermetersPlaces, on_delete=PROTECT)  # Prevent deletion of a watermeter if it's connected to a contract    
    provider = models.ForeignKey('Provider', on_delete=PROTECT, null=True, blank=True) # Add ForeignKey to Provider

    contract_start_day = models.DateTimeField()
    contract_end_day = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'Contracts'  # Specify the existing table name
        #unique_together = (('customer', 'watermeters_places'),)  # Ensure unique combination of customer and watermeters_places


class WaterConsumption(models.Model):
    water_consumption_id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)  # ForeignKey to Contract
    reading_datetime = models.DateTimeField()
    reading_value = models.FloatField()
    flag = models.CharField(max_length=10, choices=[('start', 'start'), ('end', 'end'), ('pending', 'pending')])

    class Meta:
        db_table = 'Water_Consumptions'  # Specify the existing table name
        unique_together = (('contract', 'reading_datetime'),)  # Ensure unique combination of contract and reading_datetime


# ========================  NEW MODELS ========================

class Provider(models.Model):
    provider_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=100)
    PSC = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    bank = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    ICO = models.CharField(max_length=20, unique=True)
    DIC = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    court_register = models.CharField(max_length=255)

    class Meta:
        db_table = 'Providers'

    def __str__(self):
        return self.name


class WatermeterReadingHistory(models.Model):
    record_id = models.AutoField(primary_key=True)
    watermeter = models.ForeignKey(Watermeter, on_delete=models.CASCADE)  # ForeignKey to Watermeter
    value = models.FloatField()
    datetime = models.DateTimeField()

    class Meta:
        db_table = 'watermeter_reading_history'  # Update the table name
        unique_together = (('watermeter', 'datetime'),)  # Ensure unique combination of watermeter and datetime


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Add the price field
    vat = models.ForeignKey('VAT', on_delete=PROTECT)  # ForeignKey to VAT    
    contracts = models.ManyToManyField('Contract', through='ProductContract')

    class Meta:
        db_table = 'Products'

    def __str__(self):
        return self.description
    
class ProductContract(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    individual_price = models.DecimalField(max_digits=10, decimal_places=2)  # Add this field for individual price

    class Meta:
        db_table = 'Product_Contracts'
        unique_together = (('product', 'contract'),)


class VAT(models.Model):
    vat_id = models.AutoField(primary_key=True)
    value = models.FloatField()
    vat_koeficient = models.FloatField()

    class Meta:
        db_table = 'VATs'

    def __str__(self):
        return f"{self.value}%"
