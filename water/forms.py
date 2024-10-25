# water/forms.py
from django import forms # type: ignore
from .models import (Contract, WaterConsumption, Customer, Place, Watermeter, 
                     WatermetersPlaces,  Product, Provider, VAT, ProductContract)
from django.db.models import Q  # type: ignore # Ensure Q is imported for complex queries
from django.utils import timezone  # Import timezone to get the current datetime

class VATForm(forms.ModelForm):
    class Meta:
        model = VAT
        fields = ['value', 'vat_koeficient']

class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['name', 'street', 'PSC', 'city', 'bank', 'phone', 'ICO', 'DIC', 'email', 'court_register']
    ICO = forms.CharField(required=False)
    DIC = forms.CharField(required=False)
    court_register = forms.CharField(required=False)        

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['description', 'vat', 'price']


class FinishContractForm(forms.ModelForm):
    # Field to pre-fill with the pending reading value
    reading_value = forms.FloatField(label='Final Reading Value')

    class Meta:
        model = Contract
        fields = ['contract_end_day', 'reading_value']
        widgets = {
            'contract_end_day': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        # Get the contract instance
        contract = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        # Prefill contract_end_day with the current date and time if not already set
        if not self.fields['contract_end_day'].initial:
            self.fields['contract_end_day'].initial = timezone.now()

        # Prefill reading_value from the pending water consumption entry, if it exists
        if contract:
            pending_consumption = WaterConsumption.objects.filter(contract=contract, flag='pending').first()
            if pending_consumption:
                self.fields['reading_value'].initial = pending_consumption.reading_value


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'family_name', 'street', 'street_no', 'city', 'zip', 'email', 'phone']

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['place_name', 'street', 'street_no', 'city']

class WatermeterForm(forms.ModelForm):  # Ensure this is defined
    class Meta:
        model = Watermeter
        fields = ['sn', 'mbus_adr', 'recent_reading', 'date_of_recent_reading']
        widgets = {
            'date_of_recent_reading': forms.DateTimeInput(attrs={'type': 'datetime-local'})  # For datetime picker
        }

class WatermeterPlaceForm(forms.ModelForm):
    class Meta:
        model = WatermetersPlaces
        fields = ['watermeter', 'place']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter watermeters that are not already connected to a place
        self.fields['watermeter'].queryset = Watermeter.objects.filter(
            watermetersplaces__isnull=True  # Watermeters without any connection in WatermetersPlaces
        )
        
        # Filter places that are not already connected to a watermeter
        self.fields['place'].queryset = Place.objects.filter(
            watermetersplaces__isnull=True  # Places without any connection in WatermetersPlaces
        )


class ContractForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Allow multi-select of products
        required=False  # Allow no products to be selected
    )

    class Meta:
        model = Contract
        fields = ['customer', 'watermeters_places', 'contract_start_day', 'contract_end_day']
        widgets = {
            'contract_start_day': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'contract_end_day': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract_start_day'].initial = timezone.now()
        
        # Dynamically create price fields for each product
        for product in Product.objects.all():
            self.fields[f'price_{product.product_id}'] = forms.DecimalField(
                label=f'Price for {product.description}',
                initial=product.price,
                required=True
            )

    def save(self, commit=True):
        contract = super().save(commit=False)
        if commit:
            contract.save()
            selected_products = self.cleaned_data['products']
            
            # Save the prices for each selected product
            for product in selected_products:
                price_field_name = f'price_{product.id}'
                individual_price = self.cleaned_data[price_field_name]

                # Save to ProductContract
                ProductContract.objects.create(
                    product=product,
                    contract=contract,
                    individual_price=individual_price
                )
        return contract


class ProductContractForm(forms.ModelForm):
    class Meta:
        model = ProductContract
        fields = ['product', 'individual_price']
        labels = {
            'product': 'Product',
            'individual_price': 'Individual Price'
        }


class WaterConsumptionForm(forms.ModelForm):
    class Meta:
        model = WaterConsumption
        fields = ['reading_datetime', 'reading_value']
        widgets = {
            'reading_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the initial value of reading_datetime to the current datetime
        self.fields['reading_datetime'].initial = timezone.now()

class CombinedContractForm(forms.Form):
    contract_form = ContractForm()
    water_consumption_form = WaterConsumptionForm()

