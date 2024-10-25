# water/management/commands/finish_water_consumption_period.py
from django.core.management.base import BaseCommand
from water.utils import complete_water_consumption_period  # Correct import with renamed function

class Command(BaseCommand):
    help = "Finish the water consumption period for a selected contract."

    def add_arguments(self, parser):
        parser.add_argument('contract_id', type=int, help="ID of the contract")

    def handle(self, *args, **kwargs):
        contract_id = kwargs['contract_id']

        # Call the utility function and print the result
        result_message = complete_water_consumption_period(contract_id)
        if "Successfully" in result_message:
            self.stdout.write(self.style.SUCCESS(result_message))
        else:
            self.stdout.write(self.style.WARNING(result_message))
