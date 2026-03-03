from django import forms
from .models import Lead, Followup, Activity

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'name', 'phone', 'alternate_phone', 'city','email', 'source',
            'property_type', 'bhk', 'location_preference',
            'budget_min', 'budget_max', 'purpose', 'timeline',
            'pipeline', 'temperature', 'lost_reason',
            'site_visit_date', 'site_visit_done', 'site_visit_feedback',
            'brochure_sent', 'price_list_sent', 'agreement_done',
            'notes', 'assigned_to'
        ]
        widgets = {
            'site_visit_date': forms.DateInput(attrs={'type': 'date'}),
        }

class FollowupForm(forms.ModelForm):
    class Meta:
        model = Followup
        fields = ['date', 'time', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add activity note...'})
        }