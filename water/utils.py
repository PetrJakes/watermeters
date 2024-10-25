from django.utils import timezone
from datetime import timedelta
from .models import WaterConsumption, Contract

def complete_water_consumption_period(contract_id):
    # Get the contract
    contract = Contract.objects.filter(pk=contract_id).first()
    if not contract:
        return "Contract does not exist."

    # Locate the pending water consumption record
    pending_consumption = WaterConsumption.objects.filter(contract=contract, flag="pending").first()
    if not pending_consumption:
        return "No pending water consumption record found for this contract."

    # Get the current datetime
    current_datetime = timezone.now()

    # Insert the first new record with reading_datetime set to current_datetime + 1 second, flag as "start"
    WaterConsumption.objects.create(
        contract=contract,
        reading_datetime=current_datetime + timedelta(seconds=1),
        reading_value=pending_consumption.reading_value,
        flag="start"
    )

    # Insert the second new record with reading_datetime set to current_datetime + 2 seconds, flag as "pending"
    WaterConsumption.objects.create(
        contract=contract,
        reading_datetime=current_datetime + timedelta(seconds=2),
        reading_value=pending_consumption.reading_value,
        flag="pending"
    )

    # Update the original pending record to set reading_datetime to current_datetime and flag to "end"
    pending_consumption.reading_datetime = current_datetime
    pending_consumption.flag = "end"
    pending_consumption.save()

    return "Successfully finished water consumption period."
