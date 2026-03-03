from django.db import models
from django.contrib.auth.models import User

class Lead(models.Model):

    # Pipeline stages
    PIPELINE_CHOICES = (
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Site Visit Scheduled', 'Site Visit Scheduled'),
        ('Site Visit Done', 'Site Visit Done'),
        ('Negotiation', 'Negotiation'),
        ('Closed Won', 'Closed Won'),
        ('Closed Lost', 'Closed Lost'),
    )

    # Temperature
    TEMP_CHOICES = (
        ('Hot', 'Hot'),
        ('Warm', 'Warm'),
        ('Cold', 'Cold'),
        ('Dead', 'Dead'),
    )

    # Lead Source
    SOURCE_CHOICES = (
        ('Facebook', 'Facebook'),
        ('Google', 'Google'),
        ('99acres', '99acres'),
        ('MagicBricks', 'MagicBricks'),
        ('Reference', 'Reference'),
        ('Walk-in', 'Walk-in'),
        ('Hoarding', 'Hoarding'),
        ('Other', 'Other'),
    )

    # Property Type
    PROPERTY_CHOICES = (
        ('Flat', 'Flat'),
        ('Villa', 'Villa'),
        ('Plot', 'Plot'),
        ('Commercial', 'Commercial'),
        ('Office', 'Office'),
        ('Shop', 'Shop'),
        ('Other', 'Other'),
    )

    # BHK
    BHK_CHOICES = (
        ('1 BHK', '1 BHK'),
        ('2 BHK', '2 BHK'),
        ('3 BHK', '3 BHK'),
        ('4 BHK', '4 BHK'),
        ('5 BHK', '5 BHK'),
        ('NA', 'NA'),
    )

    # Purpose
    PURPOSE_CHOICES = (
        ('Self Use', 'Self Use'),
        ('Investment', 'Investment'),
        ('Rental', 'Rental'),
    )

    # Timeline
    TIMELINE_CHOICES = (
        ('Immediate', 'Immediate'),
        ('1-3 Months', '1-3 Months'),
        ('3-6 Months', '3-6 Months'),
        ('6-12 Months', '6-12 Months'),
        ('Just Exploring', 'Just Exploring'),
    )

    # Lost Reason
    LOST_CHOICES = (
        ('Budget Issue', 'Budget Issue'),
        ('Location Issue', 'Location Issue'),
        ('Went to Competitor', 'Went to Competitor'),
        ('Not Interested', 'Not Interested'),
        ('No Response', 'No Response'),
    )

    # Basic Info
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='Other')

    # Requirement
    property_type = models.CharField(max_length=50, choices=PROPERTY_CHOICES, blank=True, null=True)
    bhk = models.CharField(max_length=20, choices=BHK_CHOICES, blank=True, null=True)
    location_preference = models.CharField(max_length=100, blank=True, null=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, blank=True, null=True)
    timeline = models.CharField(max_length=50, choices=TIMELINE_CHOICES, blank=True, null=True)

    # Status
    pipeline = models.CharField(max_length=50, choices=PIPELINE_CHOICES, default='New')
    temperature = models.CharField(max_length=10, choices=TEMP_CHOICES, default='Cold')
    lost_reason = models.CharField(max_length=50, choices=LOST_CHOICES, blank=True, null=True)

    # Site Visit
    site_visit_date = models.DateField(blank=True, null=True)
    site_visit_done = models.BooleanField(default=False)
    site_visit_feedback = models.TextField(blank=True, null=True)

    # Documents
    brochure_sent = models.BooleanField(default=False)
    price_list_sent = models.BooleanField(default=False)
    agreement_done = models.BooleanField(default=False)

    # Notes
    notes = models.TextField(blank=True, null=True)

    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_leads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Followup(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.name} - {self.date}"


class Activity(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.name} - {self.created_at}"