from django.core.management.base import BaseCommand, CommandError
from publicweb.models import HatResultsDatabase, HouseIdLookup, LsoaDomesticEnergyConsumption, PostcodeOaLookup, HatMeasuresList, EcoEligible

class Command(BaseCommand):
    help = 'Creates a fixture containing 50 rows from large tables'

    def handle(self, *args, **options):
        query_hatresultsdatabase = HatResultsDatabase.objects.all()[:50]
        query_hathouseidlookup = HouseIdLookup.objects.all()[:50]
        query_lsoadomestic = LsoaDomesticEnergyConsumption.objects.all()[:50]
        query_postcodeoalookup = PostcodeOaLookup.objects.all()[:50]
        query_ecoeligible = EcoEligible.objects.all()[:50]

        to_write = {
            '1': {
                'file_name': 'hatresults50.json',
                'query': query_hatresultsdatabase,
                },
            '2': {
                'file_name': 'hathouseidlookup50.json',
                'query': query_hathouseidlookup,
            },
            '3': {
                'file_name': 'lsoadomestic50.json',
                'query': query_lsoadomestic
            },
            '4': {
                'file_name': 'postcodeoalookup50.json',
                'query': query_postcodeoalookup
            },
            '5': {
                'file_name': 'ecoeligible50.json',
                'query': query_ecoeligible
            },
        }

        from django.core import serializers

        for k, results in to_write.iteritems():
            
            data = serializers.serialize("json", results['query'])

            file_name = "../publicweb/fixtures/" + results['file_name']
            f = open(file_name, 'w')
            f.write(data)
            f.close()
            self.stdout.write("Wrote fixture " + results['file_name'])
