from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ApplicationForm
from .models import Company, Job


def job_list(request):
    search_query = request.GET.get('q', '').strip()
    selected_company = request.GET.get('company', '').strip()
    selected_location = request.GET.get('location', '').strip()
    selected_job_type = request.GET.get('job_type', '').strip()
    selected_work_mode = request.GET.get('work_mode', '').strip()

    jobs = Job.objects.select_related('company').all()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query)
            | Q(company__name__icontains=search_query)
            | Q(company__description__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(job_type__icontains=search_query)
            | Q(work_mode__icontains=search_query)
        )

    if selected_company:
        if selected_company.isdigit():
            jobs = jobs.filter(company_id=int(selected_company))
        else:
            # Keeps older bookmarked/filter URLs with company names working.
            jobs = jobs.filter(company__name__iexact=selected_company)

    if selected_location:
        jobs = jobs.filter(location__iexact=selected_location)

    if selected_job_type:
        jobs = jobs.filter(job_type=selected_job_type)

    if selected_work_mode:
        jobs = jobs.filter(work_mode=selected_work_mode)

    paginator = Paginator(jobs, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)

    context = {
        'jobs': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'result_count': paginator.count,
        'search_query': search_query,
        'selected_company': selected_company,
        'selected_location': selected_location,
        'selected_job_type': selected_job_type,
        'selected_work_mode': selected_work_mode,
        'companies': Company.objects.order_by('name'),
        'locations': Job.objects.order_by('location').values_list('location', flat=True).distinct(),
        'job_type_choices': Job.JobType.choices,
        'work_mode_choices': Job.WorkMode.choices,
        'pagination_query': query_params.urlencode(),
        'is_filtered': bool(
            search_query
            or selected_company
            or selected_location
            or selected_job_type
            or selected_work_mode
        ),
    }
    return render(request, 'job_portal/job_list.html', context)


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)
    return render(request, 'job_portal/job_detail.html', {'job': job})


def apply_to_job(request, pk):
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            return redirect(reverse('application_success') + f'?job={job.pk}')
    else:
        form = ApplicationForm()

    return render(request, 'job_portal/application_form.html', {'form': form, 'job': job})


def application_success(request):
    job = None
    job_pk = request.GET.get('job')
    if job_pk:
        job = Job.objects.select_related('company').filter(pk=job_pk).first()
    return render(request, 'job_portal/application_success.html', {'job': job})
