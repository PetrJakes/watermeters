# water/views.py
from django.db import transaction
from django.db.models import ProtectedError # type: ignore # type: ignore
from django.forms import inlineformset_factory
from .forms import ContractForm 
from django.db import IntegrityError
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from .models import (WaterConsumption, Contract, Customer, Place, 
                     Watermeter, WatermetersPlaces, 
                     Product, Provider,ProductContract,VAT)

from .forms import (ProductForm, ProviderForm, VATForm, CustomerForm, 
                    FinishContractForm, PlaceForm, WatermeterForm, 
                    WatermeterPlaceForm, ContractForm, WaterConsumptionForm,
                    ProductContractForm)

from datetime import timedelta  # Import timedelta to add time
from datetime import datetime
from rest_framework.decorators import api_view # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from django.db.models import Case, When, Value, IntegerField

# VAT Views
def vat_list(request):
    vats = VAT.objects.all()
    return render(request, 'water/vat_list.html', {'vats': vats})

def add_vat(request):
    if request.method == 'POST':
        form = VATForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vat_list')
    else:
        form = VATForm()
    return render(request, 'water/vat_add.html', {'form': form})

def edit_vat(request, pk):
    vat = get_object_or_404(VAT, pk=pk)
    if request.method == 'POST':
        form = VATForm(request.POST, instance=vat)
        if form.is_valid():
            form.save()
            return redirect('vat_list')
    else:
        form = VATForm(instance=vat)
    return render(request, 'water/vat_edit.html', {'form': form})

def delete_vat(request, pk):
    vat = get_object_or_404(VAT, pk=pk)
    if request.method == 'POST':
        vat.delete()
        return redirect('vat_list')
    return render(request, 'water/vat_delete.html', {'vat': vat})


# Provider Views
def provider_list(request):
    providers = Provider.objects.all()
    return render(request, 'water/provider_list.html', {'providers': providers})

def add_provider(request):
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('provider_list')
    else:
        form = ProviderForm()
    return render(request, 'water/provider_add.html', {'form': form})

def edit_provider(request, pk):
    provider = get_object_or_404(Provider, pk=pk)
    if request.method == 'POST':
        form = ProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return redirect('provider_list')
    else:
        form = ProviderForm(instance=provider)
    return render(request, 'water/provider_edit.html', {'form': form})

def delete_provider(request, pk):
    provider = get_object_or_404(Provider, pk=pk)
    if request.method == 'POST':
        provider.delete()
        return redirect('provider_list')
    return render(request, 'water/provider_delete.html', {'provider': provider})


# Product Views
def product_list(request):
    products = Product.objects.all()  # This includes price, vat, description, etc.
    return render(request, 'water/product_list.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'water/product_add.html', {'form': form})

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'water/product_edit.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'water/product_delete.html', {'product': product})


@api_view(['POST'])
def update_reading(request):
    try:
        watermeter = Watermeter.objects.get(sn=request.data['sn'])  # Get watermeter by serial number (sn)
        watermeter.recent_reading = request.data['recent_reading']  # Update recent reading
        #watermeter.date_of_recent_reading = request.data['date_of_recent_reading']  # Update reading date
        watermeter.save()  # Save the watermeter
        return Response({'status': 'reading updated'}, status=status.HTTP_200_OK)
    except Watermeter.DoesNotExist:
        return Response({'error': 'Watermeter not found'}, status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


from django.utils import timezone  # Ensure timezone is imported

def finish_contract(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    if request.method == 'POST':
        finish_contract_form = FinishContractForm(request.POST, instance=contract)
        if finish_contract_form.is_valid():
            # Save the contract's end day
            contract = finish_contract_form.save(commit=False)
            contract.contract_end_day = finish_contract_form.cleaned_data.get('contract_end_day')
            contract.save()

            # Update the pending WaterConsumption record
            pending_detail = WaterConsumption.objects.filter(contract=contract, flag='pending').first()
            if pending_detail:
                pending_detail.reading_value = finish_contract_form.cleaned_data.get('reading_value')
                pending_detail.flag = 'end'
                pending_detail.save()

            return redirect('contract_list')
    else:
        # Set the initial end day to the current date and time
        finish_contract_form = FinishContractForm(instance=contract, initial={
            'contract_end_day': timezone.now()
        })

    return render(request, 'water/contract_finish.html', {
        'contract': contract,
        'finish_contract_form': finish_contract_form,
    })





def active_contracts(request):
    # Fetch contracts where contract_end_day is null
    contracts = Contract.objects.filter(contract_end_day__isnull=True).select_related('customer', 'watermeters_places')
    data = []

    for contract in contracts:
        start_detail = contract.waterconsumption_set.filter(flag='start').first()
        pending_detail = contract.waterconsumption_set.filter(flag='pending').first()

        if start_detail and pending_detail:
            if start_detail.reading_value == pending_detail.reading_value:
                difference = 0
            else:
                difference = pending_detail.reading_value - start_detail.reading_value
        else:
            difference = None

        data.append({
            'contract': contract,
            'start_detail': start_detail,
            'pending_detail': pending_detail,
            'difference': difference
        })

    return render(request, 'water/contracts_active_list.html', {
        'contracts': data
    })


def contract_list(request):
    # Annotate to ensure contracts without 'contract_end_day' come first, then sort by 'contract_start_day' descending
    contracts = Contract.objects.annotate(
        is_active=Case(
            When(contract_end_day__isnull=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-is_active', '-contract_start_day')
    return render(request, 'water/contract_list.html', {'contracts': contracts})

ProductContractFormSet = inlineformset_factory(
    Contract,
    ProductContract,
    form=ProductContractForm,
    extra=1,  # Adjust this number based on your needs
    can_delete=True  # Allow deletion of product contracts
)

def add_contract(request):
    if request.method == 'POST':
        # Debugging: Print out products and their IDs
        # for product in Product.objects.all():
        #     print(f"Product ID: {product.product_id}, Description: {product.description}")

        # print("POST data:", request.POST)  # Debugging        
        # print("Selected products:", request.POST.getlist('products'))  # Debugging the selected products list
        # Create form instances with POST data
        contract_form = ContractForm(request.POST)
        water_consumption_form = WaterConsumptionForm(request.POST)
        # print("contract_form", contract_form)
        # print("water_consumption_form", water_consumption_form)

        if contract_form.is_valid() and water_consumption_form.is_valid():
            # print("valid Cleaned data:", contract_form.cleaned_data)  # Debugging
            # Save the contract instance, but don't commit to the database yet
            contract = contract_form.save(commit=False)
            contract.save()  # Save the contract to the database

            # Save the water consumption instance (first record with 'start' flag)
            water_consumption_data = water_consumption_form.cleaned_data
            reading_datetime = water_consumption_data['reading_datetime']
            reading_value = water_consumption_data['reading_value']

            # Insert the first water consumption record with the flag 'start'
            WaterConsumption.objects.create(
                contract=contract,
                reading_datetime=reading_datetime,
                reading_value=reading_value,
                flag='start'
            )

            # Insert the second water consumption record with the flag 'pending'
            # Add 1 second to the reading_datetime to avoid the UNIQUE constraint violation
            second_reading_datetime = reading_datetime + timedelta(seconds=1)
            WaterConsumption.objects.create(
                contract=contract,
                reading_datetime=second_reading_datetime,  # Increment by 1 second
                reading_value=reading_value,  # Same reading value
                flag='pending'
            )

            # Now handle the products and their prices
            selected_products = contract_form.cleaned_data['products']
            for product in selected_products:
                price_field_name = f'price_{product.product_id}'
                individual_price = contract_form.cleaned_data.get(price_field_name)

                # Save the product prices to the ProductContract table
                ProductContract.objects.create(
                    product=product,
                    contract=contract,
                    individual_price=individual_price
                )

            # Redirect to contract list after successful saving
            return redirect('contract_list')
        else:
            # Log errors for debugging and re-render the form with errors
            print("Contract form errors:", contract_form.errors)
            print("Water consumption form errors:", water_consumption_form.errors)
            print("NOTvalid Cleaned data:", contract_form.cleaned_data)  # Debugging
            print("ERROR Selected products:", request.POST.getlist('products'))  # Debugging the selected products list

            # Re-render the form with errors, including the selected products
            selected_products = request.POST.getlist('products')
            return render(request, 'water/contract_add.html', {
                'contract_form': contract_form,
                'water_consumption_form': water_consumption_form,
                'product_price_fields': get_product_price_fields(contract_form),
                'selected_products': selected_products,  # Pass selected products to template
            })

    else:
        # Filter `WatermetersPlaces` that are connected to a contract and do not have a 'pending' WaterConsumption record
        available_places = WatermetersPlaces.objects.exclude(
            contract__waterconsumption__flag='pending'
        )
        
        # Instantiate forms and update the queryset for `watermeters_places`
        contract_form = ContractForm()
        contract_form.fields['watermeters_places'].queryset = available_places
        
        water_consumption_form = WaterConsumptionForm()
        selected_products = []  # No products selected by default

    # Prepare the product checkboxes and corresponding price fields
    product_price_fields = get_product_price_fields(contract_form)

    return render(request, 'water/contract_add.html', {
        'contract_form': contract_form,
        'water_consumption_form': water_consumption_form,
        'product_price_fields': product_price_fields,
        'selected_products': selected_products,  # Pass selected products for the template
    })





def get_product_price_fields(contract_form):
    """
    Helper function to dynamically create the product price fields.
    """
    product_price_fields = []
    for product in Product.objects.all():
        price_field_name = f'price_{product.product_id}'
        price_field = contract_form[price_field_name]
        product_price_fields.append((product, price_field))
    return product_price_fields


# View for editing a contract
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    water_consumption = WaterConsumption.objects.filter(contract=contract).first()  # Fetch the associated water consumption

    # Fetch all ProductContract records related to this contract
    product_contracts = ProductContract.objects.filter(contract=contract)

    if request.method == 'POST':
        contract_form = ContractForm(request.POST, instance=contract)
        water_consumption_form = WaterConsumptionForm(request.POST, instance=water_consumption)

        if contract_form.is_valid() and water_consumption_form.is_valid():
            contract = contract_form.save(commit=False)
            contract.save()

            # Update water consumption data
            water_consumption = water_consumption_form.save(commit=False)
            water_consumption.contract = contract
            water_consumption.save()

            # Handle selected products and their prices
            selected_products = contract_form.cleaned_data['products']
            ProductContract.objects.filter(contract=contract).delete()  # Clear old product entries
            for product in selected_products:
                price_field_name = f'price_{product.product_id}'
                individual_price = contract_form.cleaned_data.get(price_field_name)

                # Save the product prices to the ProductContract table
                ProductContract.objects.create(
                    product=product,
                    contract=contract,
                    individual_price=individual_price
                )

            return redirect('contract_list')  # Redirect after successful save
        else:
            selected_products = request.POST.getlist('products')  # Preserve selected products on error
    else:
        contract_form = ContractForm(instance=contract)
        water_consumption_form = WaterConsumptionForm(instance=water_consumption)

        # Get the products associated with this contract from ProductContract and pre-fill individual prices
        selected_products = product_contracts.values_list('product_id', flat=True)

        # Prefill the form with the prices from the ProductContract table
        for product_contract in product_contracts:
            price_field_name = f'price_{product_contract.product.product_id}'
            contract_form.fields[price_field_name].initial = product_contract.individual_price

    # Prepare the product checkboxes and corresponding price fields
    product_price_fields = get_product_price_fields(contract_form)

    return render(request, 'water/contract_edit.html', {
        'contract_form': contract_form,
        'water_consumption_form': water_consumption_form,
        'product_price_fields': product_price_fields,
        'selected_products': selected_products,  # Pass selected products to prefill
    })



# View for deleting a contract
def delete_contract(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    if request.method == 'POST':
        contract.delete()
        return redirect('contract_list')  # Redirect to the list after deleting

    return render(request, 'water/contract_delete.html', {'contract': contract})


def watermeter_place_list(request):
    # Query all watermeter places and annotate their associated contract, if any
    watermeter_places = WatermetersPlaces.objects.prefetch_related('contract_set').all()

    # Prepare a list of watermeter places with their associated contract, if it exists
    connections = []
    for watermeter_place in watermeter_places:
        contract = Contract.objects.filter(watermeters_places=watermeter_place).first()  # Get the associated contract, if any
        connections.append({
            'watermeter_place': watermeter_place,
            'contract': contract  # Contract can be None if there is no contract for that place
        })

    return render(request, 'water/watermeter_place_list.html', {'connections': connections})


def add_watermeter_place(request):
    if request.method == 'POST':
        form = WatermeterPlaceForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new connection between watermeter and place
            return redirect('watermeter_place_list')  # Redirect to the list after adding
    else:
        form = WatermeterPlaceForm()  # Create an empty form for GET requests

    # Render the form template to add a new connection
    return render(request, 'water/watermeter_place_connect.html', {'form': form})


def edit_watermeter_place(request, connection_id):
    watermeter_place = get_object_or_404(WatermetersPlaces, pk=connection_id)

    if request.method == 'POST':
        form = WatermeterPlaceForm(request.POST, instance=watermeter_place)
        if form.is_valid():
            form.save()
            return redirect('watermeter_place_list')
    else:
        form = WatermeterPlaceForm(instance=watermeter_place)

    return render(request, 'water/watermeter_place_edit.html', {'form': form})

def delete_watermeter_place(request, connection_id):
    watermeter_place = get_object_or_404(WatermetersPlaces, pk=connection_id)

    if request.method == 'POST':
        watermeter_place.delete()
        return redirect('watermeter_place_list')

    return render(request, 'water/watermeter_place_delete.html', {'watermeter_place': watermeter_place})

def connect_watermeter_place(request):
    if request.method == 'POST':
        form = WatermeterPlaceForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new watermeter-place connection
            return redirect('watermeter_place_list')  # Redirect to the list after saving
    else:
        form = WatermeterPlaceForm()  # Create an empty form for GET requests

    # Render the form template to connect a watermeter and a place
    return render(request, 'water/watermeter_place_connect.html', {'form': form})

def customer_list(request):
    customers = Customer.objects.all().order_by('family_name')  # Get all customers
    return render(request, 'water/customer_list.html', {'customers': customers})

def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()  # Save the updated customer instance
            return redirect('customer_list')  # Redirect to the customer list page
    else:
        form = CustomerForm(instance=customer)  # Prepopulate the form with the customer's current data

    return render(request, 'water/customer_form.html', {'form': form})

def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect after successful addition
    else:
        form = CustomerForm()
    return render(request, 'water/customer_add.html', {'form': form})

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)  # Get the customer or return a 404 if not found
    if request.method == "POST":
        customer.delete()  # Delete the customer
        return redirect('customer_list')  # Redirect to the customer list after deletion
    return render(request, 'water/customer_delete.html', {'customer': customer})  # Render confirmation page

# Add a main page view if necessary
def main_page(request):
    return render(request, 'water/main_page.html')  # Create a template for the main page


def place_list(request):
    places = Place.objects.all()  # Get all places
    return render(request, 'water/place_list.html', {'places': places})  # Render the template

def add_place(request):
    if request.method == 'POST':
        form = PlaceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('place_list')
    else:
        form = PlaceForm()
    return render(request, 'water/place_add.html', {'form': form})


def edit_place(request, place_id):
    place = get_object_or_404(Place, pk=place_id)  # Get the Place instance
    
    if request.method == 'POST':
        form = PlaceForm(request.POST, instance=place)  # Bind form with POST data
        if form.is_valid():  # Check if the form is valid
            form.save()  # Save the updated place
            return redirect('place_list')  # Redirect to the place list
    else:
        form = PlaceForm(instance=place)  # Load form with existing place data

    return render(request, 'water/place_form.html', {'form': form})  # Render the form template


def delete_place(request, place_id):
    place = get_object_or_404(Place, pk=place_id)

    if request.method == 'POST':
        try:
            place.delete()
            return redirect('place_list')  # Redirect to the list after successful deletion
        except ProtectedError:
            # Handle the ProtectedError and provide a user-friendly message
            return render(request, 'water/place_delete.html', {
                'place': place,
                'error_message': "Cannot delete this place because it is connected to an active contract."
            })

    return render(request, 'water/place_delete.html', {'place': place})


# Water Meter views
def watermeter_list(request):
    watermeters = Watermeter.objects.all()  # Fetch all water meters from the database
    return render(request, 'water/watermeter_list.html', {'watermeters': watermeters})

def add_watermeter(request):
    if request.method == 'POST':
        form = WatermeterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('watermeter_list')
    else:
        form = WatermeterForm()
    return render(request, 'water/watermeter_add.html', {'form': form})

def edit_watermeter(request, watermeter_id):
    watermeter = get_object_or_404(Watermeter, pk=watermeter_id)

    if request.method == 'POST':
        form = WatermeterForm(request.POST, instance=watermeter)
        if form.is_valid():
            form.save()  # This will save the updated data to the database
            return redirect('watermeter_list')
    else:
        form = WatermeterForm(instance=watermeter)  # Initialize form with existing watermeter data

    return render(request, 'water/watermeter_form.html', {'form': form})

def delete_watermeter(request, watermeter_id):
    watermeter = get_object_or_404(Watermeter, watermeter_id=watermeter_id)
    if request.method == "POST":
        watermeter.delete()
        return redirect('watermeter_list')  # Redirect after deletion
    return render(request, 'water/watermeter_delete.html', {'watermeter': watermeter})

