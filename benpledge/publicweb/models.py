from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import Signal
from django.dispatch import receiver
from django.core.mail import send_mail
from datetime import datetime
from PIL import Image

from registration.signals import user_registered
from geoposition.fields import GeopositionField

class Measure(models.Model):
    """A retrofit measure. If no HAT information is available the
        values in this model are used to calculate energy savings. """
    name = models.CharField(max_length=75)
    description = models.TextField(default='No description available.')
    hat_measure = models.OneToOneField('HatMeasuresList', null=True,
        blank=True)
    measure_image_1 = models.ImageField(null=True, blank=True,
        upload_to='measures_%Y/%m_%d')
    estimated_annual_energy_savings_kwh = models.IntegerField(null=True,
        blank=True)
    estimated_annual_cost_savings = models.FloatField(null=True, blank=True)
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    SIZE_CHOICES = (
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
        )
    size = models.IntegerField(choices=SIZE_CHOICES, default = 1)

    def __unicode__(self):
        return self.name

class Provider(models.Model):
    """Displayed as an advert next to measure pages"""
    name = models.CharField(max_length=75)
    description = models.TextField(default='No description available.')
    website = models.URLField(blank=True, null=True)
    measures = models.ManyToManyField(Measure, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to='providers_%Y/%m%d')
    ORDER_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
    )
    order = models.IntegerField(choices=ORDER_CHOICES, default=1)
    display_on_measure_pages = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class AboutPage(models.Model):
    """Title and text of /about/ """
    title = models.CharField(max_length=100)
    description = models.TextField(default='No about text.')

    def __unicode__(self):
        return self.title

class FundingOption(models.Model):
    """Details are displayed on the right of the 'All Measures' page"""
    name = models.CharField(max_length=100)
    description = models.TextField(default='No description available.')

    def __unicode__(self):
        return self.name

class Organisation(models.Model):
    """For /help/ - local energy groups """
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description available.")
    website = models.URLField()
    logo = models.ImageField(null=True, blank=True, upload_to='logos%Y/%m/%d')
    LOCAL = 1
    CITY_WIDE = 2
    NATIONAL = 3
    TYPE_CHOICES = (
        (LOCAL, 'Local'),
        (CITY_WIDE, 'City wide'),
        (NATIONAL, 'National'),
        )
    organisation_type = models.IntegerField(choices=TYPE_CHOICES,
        default=LOCAL)

    def __unicode__(self):
        return self.name

class TopTip(models.Model):
    """TopTips are displayed after people click 'get started'"""
    name = models.CharField(max_length=100)
    description = models.TextField(default='No description available.', null=True, blank=True)
    measure_id = models.ForeignKey(Measure, null=True, blank=True)
    display_on_welcome_screen = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

class HomepageCheckList(models.Model):
    """Entries appear in 'Are you...' list one homepage"""
    ORDER_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        )
    order = models.IntegerField(choices=ORDER_CHOICES, default=1)
    text = models.CharField(max_length=150)

    def __unicode__(self):
        return str(self.order) + ' - ' + self.text

class Pledge(models.Model):
    """Holds pledges and pledge feedback
        hat_results is set to the HAT results for the pledge
        of this measure at the time of pledging
    """
    measure = models.ForeignKey(Measure)
    user = models.ForeignKey(User)#, related_name='pledge')
    deadline = models.DateField(null=True, blank=True)
    date_made = models.DateTimeField(default=datetime.now)
    hat_results = models.ForeignKey('HatResultsDatabase', null=True, blank=True)
    receive_updates = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    feedback = models.TextField(default='No feedback given.', blank=True, null=True)
    display_feedback_on_measure_page = models.BooleanField(default=False)

    INTEREST_ONLY = 1
    PLEDGE = 2
    PLEDGE_TYPE_CHOICES = (
        (INTEREST_ONLY, 'Interest Only'),
        (PLEDGE, 'Pledge'),
        )
    pledge_type = models.IntegerField(
        choices=PLEDGE_TYPE_CHOICES,
        default=PLEDGE)

    def __unicode__(self):
        stringrep = str(self.measure) + ' - ' + str(self.user)
        if self.complete:
            stringrep += " (complete)"
        return stringrep


    def time_progress(pledge):
        # convert date to datetime
        deadline = datetime.combine(pledge.deadline, datetime.min.time())
        # make date_made naive
        date_made = pledge.date_made.replace(tzinfo=None)
        duration = deadline - date_made
        time_progress = (datetime.now()-date_made).total_seconds()/duration.total_seconds()
        time_progress *= 100
        return time_progress

class Area(models.Model):
    postcode_district = models.CharField(max_length=4)
    area_name = models.CharField(max_length=100)
    position = GeopositionField()

    def __unicode__(self):
        return self.postcode_district + " - " + self.area_name

class Dwelling(models.Model):
    """Information about a dwelling provided by a User"""
    # tenure
    OWN = 1
    PRIVATELY_RENTING = 2
    RENTING_COUNCIL_HA = 3
    UNKNOWN = 4
    TENURE_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (OWN, 'Own'),
        (PRIVATELY_RENTING, 'Privately Renting'),
        (RENTING_COUNCIL_HA, 'Renting from Council or Housing Association')
        )
    tenure = models.IntegerField(
        choices=TENURE_CHOICES,
        null=True,
        blank=True
        )
    SINGLE_GLAZING = 1
    DOUBLE_GLAZING = 2
    WINDOW_CHOICES = (
        (SINGLE_GLAZING, 'Single glazing'),
        (DOUBLE_GLAZING, 'Double glazing')
        )
    window_type = models.IntegerField(
        choices=WINDOW_CHOICES,
        null=True,
        blank=True)
    dwelling_type = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'DwellingType'},
     related_name='hatmetadata_dwelling_type', null=True, blank=True)
    property_age = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'PropertyAge'},
     related_name='hatmetadata_property_age', null=True, blank=True)
    number_of_bedrooms = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'NumberofBedrooms'},
     related_name='hatmetadata_number_of_bedrooms', null=True, blank=True)
    heating_fuel = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'HeatingFuel'},
     related_name='hatmetadata_heating_fuel', null=True, blank=True)
    heating_type = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'HeatingType'},
     related_name='hatmetadata_heating_type', null=True, blank=True)
    loft_insulation = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'Loftinsulation'},
     related_name='hatmetadata_loft_insulation', null=True, blank=True)
    wall_type = models.ForeignKey('HatMetaData',
     limit_choices_to={'variable': 'WallType'},
     related_name='hatmetadata_wall_type', null=True, blank=True)

    street_name = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    area = models.ForeignKey(Area, null=True, blank=True)
    house_id = models.IntegerField(default=0)
    position = GeopositionField()


    number_of_inhabitants = models.IntegerField(blank=True, null=True)
    aprroximate_spent_on_gas_per_month = models.IntegerField(blank = True, null=True)
    approximate_spent_on_electricity_per_month = models.IntegerField(blank = True, null=True)
    gas_supplier = models.CharField(max_length=50, blank=True, null=True)
    electricity_supplier = models.CharField(max_length=50, blank=True, null=True)
    ENERGY_EFFICIENCY_RATING_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        )

    energy_efficiency_rating = models.CharField(choices=ENERGY_EFFICIENCY_RATING_CHOICES,
        max_length=1, blank=True, null=True)

    def __unicode__(self):
        dwelling_string = ""
        if self.street_name:
            dwelling_string += self.street_name
        if self.postcode:
            dwelling_string += ' ' + self.postcode 
        if self.area:
            dwelling_string += ' ' + self.area.postcode_district
        return dwelling_string



class UserProfile(models.Model):
    """Model links Users with Dwellings """
    user = models.OneToOneField(User)
    dwelling = models.ForeignKey(Dwelling, null=True, blank=True)

    def __unicode__(self):
        return str(self.user) + ' profile'

    @receiver(user_registered)
    def link_profile_with_user(sender, **kwargs):
        """Associates new Users with a UserProfile
            - Method called by signal from django-registration"""
        profile = UserProfile(user=kwargs['user'])
        profile.save()
        send_mail('BEN Pledge account created', 
            "Your Bristol Energy Network pledge account has been created." + 
            "You may now login using username " + str(kwargs['user']) + 
            " and the password you chose when you registered.", 'benpledgehelp@gmail.com',
            [kwargs['user'].email], fail_silently=False)

# Link django-registration 'user registered' signal with link_profile_with_user method
user_registered.connect(UserProfile.link_profile_with_user, sender=None, weak=True,
    dispatch_uid="account_registered_signal")

# CSE DATA
# These Models relate directly to tables in the original Housing Assessment Tool
class HatResultsDatabase(models.Model):
    """The largest table, links a house id and measure with measure information"""
    index = models.BigIntegerField(db_index=True)
    house_id = models.IntegerField()
    m1 = models.IntegerField() # this field is unnecessary
    current_sap_rating = models.FloatField()
    post_measure_sap_rating = models.FloatField()
    sap_change = models.FloatField()
    current_energy_consumption_kwh = models.FloatField()
    post_measure_energy_consumption_kwh = models.FloatField()
    consumption_change = models.IntegerField()
    current_energy_costs = models.DecimalField(max_digits=9, decimal_places=2)
    post_measure_energy_costs = models.DecimalField(max_digits=9, decimal_places=2)
    annual_cost_reduction = models.DecimalField(max_digits=9, decimal_places=2)
    current_co2_emissions_kgco2 = models.FloatField()
    post_measure_co2_emissions_kgco2 = models.FloatField()
    annual_co2_reduction = models.FloatField()
    approximate_installation_costs = models.DecimalField(max_digits=9, decimal_places=2)
    grean_deal = models.BooleanField()
    eco_finance = models.BooleanField()

    def __unicode__(self):
        return str(self.index)

class HouseIdLookup(models.Model):
    """Table used to convert information on a house into an ID"""
    dwelling_type = models.IntegerField()
    property_age = models.IntegerField()
    number_of_bedrooms = models.IntegerField()
    heating_fuel = models.IntegerField()
    heating_type = models.IntegerField()
    loft_insulation = models.IntegerField()
    wall_type = models.IntegerField()
    index_id = models.IntegerField(db_index=True)
    house_id = models.IntegerField()

    def __unicode__(self):
        return str(self.house_id)

class HatMeasuresList(models.Model):
    """Measures covered by HAT """
    measure_id = models.IntegerField()
    measure_name = models.CharField(max_length=8)
    measure_description = models.CharField(max_length=50)
    measure_category = models.CharField(max_length=11, null=True)
    measure_lifetime = models.IntegerField(null=True)
    measure_comfort_factor = models.FloatField(null=True)

    def __unicode__(self):
        return self.measure_description

class HatMetaData(models.Model):
    """Model contains options used in `My Home' form
         - Options available as input to HAT tool such as
           age range, fuel type, number of bedrooms
     """
    variable = models.CharField(max_length=17)
    value = models.IntegerField()
    label = models.CharField(max_length=50)

    def __unicode__(self):
        return self.label

class LsoaDomesticEnergyConsumption(models.Model):
    """DECC energy consumption by lower super output area"""
    year = models.CharField(max_length=4)
    la_code = models.CharField(max_length=9)
    msoa_code = models.CharField(max_length=9)
    msoa_name = models.CharField(max_length=20)
    lsoa_code = models.CharField(max_length=9)
    lsoa_name = models.CharField(max_length=20)
    total_electricity_and_gas_consumption_mwh = models.IntegerField()
    ordinary_electricity_consumption_mwh = models.IntegerField()
    economy_7_electricity_consumption_mwh = models.IntegerField()
    gas_consumption_mwh = models.IntegerField()
    number_of_ordinary_electricity_meters = models.IntegerField()
    average_ordinary_electricity_consumption_kwh = models.IntegerField()
    number_of_economy_7_electricity_meters = models.IntegerField()
    average_economy_7_electricity_consumption_kwh = models.IntegerField()
    number_domestic_gas_meters = models.IntegerField()
    average_domestic_gas_consumption_kwh = models.IntegerField()

class PostcodeOaLookup(models.Model):
    """Postcode lookup to get output area codes"""
    postcode = models.CharField(db_index=True, max_length=8)
    oa_code = models.CharField(max_length=9)
    lsoa_code = models.CharField(max_length=9)
    lsoa_name = models.CharField(max_length=20)
    msoa_code = models.CharField(max_length=9)
    la_code = models.CharField(max_length=9)

class EcoEligible(models.Model):
    """Lower super output areas eligible for ECO funding"""
    lsoa_code = models.CharField(max_length=9)

