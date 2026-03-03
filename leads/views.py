from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from django.http import HttpResponse
from .models import Lead, Followup, Activity
from .forms import LeadForm, FollowupForm, ActivityForm
import csv, io


def format_budget(value):
    if not value:
        return '—'
    value = int(value)
    if value >= 10000000:
        return f'₹{value/10000000:.1f}Cr'
    elif value >= 100000:
        return f'₹{value/100000:.1f}L'
    else:
        return f'₹{value:,}'

def login_view(request):
    error = None
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password'
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.is_superuser:
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.filter(assigned_to=request.user)

    today = now().date()
    today_followups = Followup.objects.filter(date=today, done=False)
    if not request.user.is_superuser:
        today_followups = today_followups.filter(lead__assigned_to=request.user)
        
    new_leads_today = leads.filter(created_at__date=today)

    return render(request, 'dashboard.html', {
        'leads': leads,
        'today_followups': today_followups,
        'new_leads_today': new_leads_today,
        'today': today,
    })

@login_required
def add_lead(request):
    form = LeadForm(request.POST or None)
    if not request.user.is_superuser:
        form.fields.pop('assigned_to')
    if form.is_valid():
        lead = form.save(commit=False)
        lead.created_by = request.user
        if not request.user.is_superuser:
            lead.assigned_to = request.user
        lead.save()
        Activity.objects.create(lead=lead, user=request.user, note='Lead created')
        return redirect('dashboard')
    return render(request, 'add_lead.html', {'form': form, 'title': 'Add Lead'})

@login_required
def edit_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadForm(request.POST or None, instance=lead)
    if not request.user.is_superuser:
        form.fields.pop('assigned_to')
    if form.is_valid():
        form.save()
        Activity.objects.create(lead=lead, user=request.user, note='Lead updated')
        return redirect('lead_detail', pk=pk)
    return render(request, 'add_lead.html', {'form': form, 'title': 'Edit Lead'})

@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    activities = lead.activities.all().order_by('-created_at')
    followups = lead.followups.all().order_by('-date')
    form = ActivityForm(request.POST or None)
    if form.is_valid():
        activity = form.save(commit=False)
        activity.lead = lead
        activity.user = request.user
        activity.save()
        return redirect('lead_detail', pk=pk)
    return render(request, 'lead_detail.html', {
        'lead': lead,
        'activities': activities,
        'followups': followups,
        'form': form,
    })

@login_required
def add_followup(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    form = FollowupForm(request.POST or None)
    if form.is_valid():
        followup = form.save(commit=False)
        followup.lead = lead
        followup.user = request.user
        followup.save()
        Activity.objects.create(lead=lead, user=request.user, note=f'Followup scheduled for {followup.date}')
        return redirect('lead_detail', pk=pk)
    return render(request, 'add_followup.html', {'form': form, 'lead': lead})

@login_required
def complete_followup(request, pk):
    followup = get_object_or_404(Followup, pk=pk)
    followup.done = True
    followup.save()
    Activity.objects.create(lead=followup.lead, user=request.user, note=f'Followup completed for {followup.date}')
    return redirect('lead_detail', pk=followup.lead.pk)

@staff_member_required
def delete_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    return redirect('dashboard')

@staff_member_required
def manage_users(request):
    users = User.objects.filter(is_superuser=False)
    return render(request, 'manage_users.html', {'users': users})

@staff_member_required
def create_user(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            error = 'Username already exists'
        else:
            User.objects.create_user(username=username, password=password)
            return redirect('manage_users')
    return render(request, 'create_user.html', {'error': error})

@staff_member_required
def import_leads(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']
        data = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(data))
        for row in reader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            lead = Lead.objects.create(
                name=row['name'],
                phone=row['phone'],
                alternate_phone=row.get('alternate_phone', ''),
                city=row.get('city', ''),
                email=row.get('email', ''),
                source=row.get('source', 'Other'),
                property_type=row.get('property_type', ''),
                bhk=row.get('bhk', ''),
                location_preference=row.get('location_preference', ''),
                budget_min=row.get('budget_min') or None,
                budget_max=row.get('budget_max') or None,
                pipeline=row.get('pipeline', 'New'),
                temperature=row.get('temperature', 'Cold'),
                notes=row.get('notes', ''),
                created_by=request.user,
                assigned_to=request.user
            )
            Activity.objects.create(lead=lead, user=request.user, note='Lead imported from CSV')
        return redirect('dashboard')
    return render(request, 'import_leads.html')

@staff_member_required
def export_leads(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Alternate Phone', 'City', 'Email', 'Source',
                     'Property Type', 'BHK', 'Location', 'Budget Min', 'Budget Max',
                     'Pipeline', 'Temperature', 'Notes', 'Added By', 'Assigned To', 'Created At'])
    for lead in Lead.objects.all():
        writer.writerow([
            lead.name, lead.phone,
            lead.alternate_phone or '',
            lead.city or '',
            lead.email or '',
            lead.source, lead.property_type or '',
            lead.bhk or '', lead.location_preference or '',
            lead.budget_min or '', lead.budget_max or '',
            lead.pipeline, lead.temperature,
            lead.notes or '',
            lead.created_by.username,
            lead.assigned_to.username if lead.assigned_to else '-',
            lead.created_at.strftime('%d %b %Y')
        ])
    return response

@login_required
def all_leads(request):
    if request.user.is_superuser:
        leads = Lead.objects.all().order_by('-created_at')
    else:
        leads = Lead.objects.filter(assigned_to=request.user).order_by('-created_at')

    # Filters
    pipeline = request.GET.get('pipeline', '')
    temperature = request.GET.get('temperature', '')
    source = request.GET.get('source', '')
    search = request.GET.get('search', '')

    if pipeline:
        leads = leads.filter(pipeline=pipeline)
    if temperature:
        leads = leads.filter(temperature=temperature)
    if source:
        leads = leads.filter(source=source)
    if search:
        leads = leads.filter(name__icontains=search) | leads.filter(phone__icontains=search)

    return render(request, 'all_leads.html', {
        'leads': leads,
        'pipeline_filter': pipeline,
        'temperature_filter': temperature,
        'source_filter': source,
        'search': search,
        'pipeline_choices': Lead.PIPELINE_CHOICES,
        'temperature_choices': Lead.TEMP_CHOICES,
        'source_choices': Lead.SOURCE_CHOICES,
    })

@login_required
def analytics(request):
    if request.user.is_superuser:
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.filter(assigned_to=request.user)

    from django.db.models import Count

    pipeline_data = leads.values('pipeline').annotate(count=Count('id'))
    temperature_data = leads.values('temperature').annotate(count=Count('id'))
    source_data = leads.values('source').annotate(count=Count('id'))

    total = leads.count()
    hot = leads.filter(temperature='Hot').count()
    warm = leads.filter(temperature='Warm').count()
    cold = leads.filter(temperature='Cold').count()
    won = leads.filter(pipeline='Closed Won').count()
    lost = leads.filter(pipeline='Closed Lost').count()

    return render(request, 'analytics.html', {
        'total': total,
        'hot': hot,
        'warm': warm,
        'cold': cold,
        'won': won,
        'lost': lost,
        'pipeline_data': list(pipeline_data),
        'temperature_data': list(temperature_data),
        'source_data': list(source_data),
    })