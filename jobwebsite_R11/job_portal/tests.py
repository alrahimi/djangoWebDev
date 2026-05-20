from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Application, Company, Job


class ApplicationStatusTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Example Company',
            description='Example employer for tests.',
            location='Remote',
        )
        self.job = Job.objects.create(
            title='Software Engineer',
            company=self.company,
            description='Build and maintain Django applications.',
            location='Remote',
            job_type=Job.JobType.FULL_TIME,
            work_mode=Job.WorkMode.REMOTE,
        )

    def test_new_application_defaults_to_new_status(self):
        resume = SimpleUploadedFile('resume.txt', b'Test resume content')
        application = Application.objects.create(
            job=self.job,
            applicant_name='Test Applicant',
            email='applicant@example.com',
            resume=resume,
        )

        self.assertEqual(application.status, Application.Status.NEW)
        self.assertEqual(application.get_status_display(), 'New')
        self.assertIsNotNone(application.status_updated_at)

    def test_application_status_choices_include_hiring_workflow(self):
        labels = [label for _value, label in Application.Status.choices]

        self.assertEqual(labels, ['New', 'Reviewed', 'Interview', 'Rejected', 'Hired'])


class CompanyModelTests(TestCase):
    def test_company_string_representation_uses_name(self):
        company = Company.objects.create(name='Acme Tech', location='Remote')

        self.assertEqual(str(company), 'Acme Tech')

    def test_job_string_representation_uses_company_model(self):
        company = Company.objects.create(name='Acme Tech', location='Remote')
        job = Job.objects.create(
            title='Django Developer',
            company=company,
            description='Build web applications with Python and Django.',
            location='Remote',
        )

        self.assertEqual(str(job), 'Django Developer at Acme Tech')


class JobBrowseTests(TestCase):
    def setUp(self):
        self.acme = Company.objects.create(
            name='Acme Tech',
            description='A software company focused on web platforms.',
            location='Remote',
            website='https://example.com',
        )
        self.northwind = Company.objects.create(
            name='Northwind Analytics',
            description='Analytics and operations reporting.',
            location='New York',
        )
        self.django_job = Job.objects.create(
            title='Django Developer',
            company=self.acme,
            description='Build web applications with Python and Django.',
            location='Remote',
            job_type=Job.JobType.FULL_TIME,
            work_mode=Job.WorkMode.REMOTE,
        )
        self.data_job = Job.objects.create(
            title='Data Analyst',
            company=self.northwind,
            description='Analyze hiring and operations data.',
            location='New York',
            job_type=Job.JobType.PART_TIME,
            work_mode=Job.WorkMode.ON_SITE,
        )

    def test_job_list_search_filters_by_keyword(self):
        response = self.client.get(reverse('job_list'), {'q': 'Django'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Developer')
        self.assertNotContains(response, 'Data Analyst')
        self.assertEqual(response.context['result_count'], 1)

    def test_job_list_searches_company_model_name(self):
        response = self.client.get(reverse('job_list'), {'q': 'Northwind'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Analyst')
        self.assertNotContains(response, 'Django Developer')

    def test_job_list_filters_by_company_and_location(self):
        response = self.client.get(reverse('job_list'), {
            'company': str(self.northwind.pk),
            'location': 'New York',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Analyst')
        self.assertNotContains(response, 'Django Developer')
        self.assertEqual(response.context['selected_company'], str(self.northwind.pk))
        self.assertEqual(response.context['selected_location'], 'New York')

    def test_job_list_filters_by_job_type_and_work_mode(self):
        response = self.client.get(reverse('job_list'), {
            'job_type': Job.JobType.PART_TIME,
            'work_mode': Job.WorkMode.ON_SITE,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Analyst')
        self.assertNotContains(response, 'Django Developer')

    def test_job_list_paginates_results(self):
        for index in range(7):
            Job.objects.create(
                title=f'Extra Job {index}',
                company=self.acme,
                description='Extra role for pagination testing.',
                location='Remote',
                job_type=Job.JobType.FULL_TIME,
                work_mode=Job.WorkMode.REMOTE,
            )

        response = self.client.get(reverse('job_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 6)
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertContains(response, 'Page 1 of 2')

    def test_pagination_preserves_search_parameters(self):
        for index in range(7):
            Job.objects.create(
                title=f'Python Role {index}',
                company=self.acme,
                description='Python pagination test.',
                location='Remote',
                job_type=Job.JobType.FULL_TIME,
                work_mode=Job.WorkMode.REMOTE,
            )

        response = self.client.get(reverse('job_list'), {'q': 'Python'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '?q=Python&amp;page=2')


class PublicUITests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Design Co',
            description='A small product design studio.',
            location='Hybrid',
            website='https://example.com',
        )
        self.job = Job.objects.create(
            title='Frontend Developer',
            company=self.company,
            description='Build polished user interfaces for a small product team.',
            location='Hybrid',
            job_type=Job.JobType.CONTRACT,
            work_mode=Job.WorkMode.HYBRID,
        )

    def test_base_navigation_appears_on_job_list_without_public_admin_link(self):
        response = self.client.get(reverse('job_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Job Portal')
        self.assertContains(response, 'Jobs')
        self.assertNotContains(response, '>Admin<')

    def test_job_list_uses_job_card_content(self):
        response = self.client.get(reverse('job_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find your next role')
        self.assertContains(response, 'Design Co')
        self.assertContains(response, 'Contract')
        self.assertContains(response, 'Hybrid')
        self.assertContains(response, 'View details')

    def test_job_detail_shows_company_information_and_no_account_required(self):
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No account is required')
        self.assertContains(response, 'Apply for this job')
        self.assertContains(response, 'About Design Co')
        self.assertContains(response, 'Company website')

    def test_application_form_shows_selected_job_summary(self):
        response = self.client.get(reverse('apply_to_job', kwargs={'pk': self.job.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Selected job')
        self.assertContains(response, 'Design Co')
        self.assertContains(response, 'Contract')
        self.assertContains(response, 'Tell us about yourself')
        self.assertContains(response, 'PDF, DOC, DOCX, or TXT')
