# Generated migration for multi-tenant foundation
# This adds Company, Plan, Subscription models and company_id FK to tracking tables

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_companysettings_company_name_and_more'),
    ]

    operations = [
        # Create Plan model
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('FREE', 'Free'), ('PRO', 'Professional'), ('ENTERPRISE', 'Enterprise')], max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('max_employees', models.IntegerField(default=5, help_text='Max employees allowed')),
                ('max_storage_gb', models.IntegerField(default=10, help_text='Max storage in GB')),
                ('screenshot_retention_days', models.IntegerField(default=30)),
                ('price_monthly', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['max_employees'],
            },
        ),
        
        # Create Company model
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('contact_person', models.CharField(blank=True, max_length=255)),
                ('contact_phone', models.CharField(blank=True, max_length=30)),
                ('company_key', models.CharField(db_index=True, max_length=64, unique=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('SUSPENDED', 'Suspended'), ('TRIAL', 'Trial')], default='TRIAL', max_length=20)),
                ('trial_ends_at', models.DateTimeField(blank=True, null=True)),
                ('subscription_expires_at', models.DateTimeField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('address', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_sync_at', models.DateTimeField(blank=True, help_text='Last desktop app sync', null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.plan')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # Create Subscription model
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('EXPIRED', 'Expired'), ('CANCELLED', 'Cancelled')], default='ACTIVE', max_length=20)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='core.company')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.plan')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        
        # Add company field to User model
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='core.company'),
        ),
        
        # Add OWNER role choice to User
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('OWNER', 'Software Owner'), ('ADMIN', 'Company Admin'), ('MANAGER', 'Manager'), ('EMPLOYEE', 'Employee')],
                default='EMPLOYEE',
                max_length=10
            ),
        ),
        
        # Add company field to CompanySettings
        migrations.AddField(
            model_name='companysettings',
            name='company',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='core.company'),
        ),
        
        # Add company field to WorkSession
        migrations.AddField(
            model_name='worksession',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='work_sessions', to='core.company'),
        ),
        
        # Add company field to ApplicationUsage
        migrations.AddField(
            model_name='applicationusage',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_usages', to='core.company'),
        ),
        
        # Add company field to WebsiteUsage
        migrations.AddField(
            model_name='websiteusage',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='website_usages', to='core.company'),
        ),
        
        # Add company field to ActivityLog
        migrations.AddField(
            model_name='activitylog',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to='core.company'),
        ),
        
        # Add company field to Screenshot
        migrations.AddField(
            model_name='screenshot',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='screenshots', to='core.company'),
        ),
        
        # Add company field to Task
        migrations.AddField(
            model_name='task',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.company'),
        ),
        
        # Create CompanyUsageDaily aggregate table
        migrations.CreateModel(
            name='CompanyUsageDaily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('total_active_seconds', models.IntegerField(default=0)),
                ('total_idle_seconds', models.IntegerField(default=0)),
                ('num_employees_active', models.IntegerField(default=0)),
                ('num_sessions', models.IntegerField(default=0)),
                ('num_screenshots', models.IntegerField(default=0)),
                ('storage_used_mb', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_usage', to='core.company')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('company', 'date')},
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='companyusagedaily',
            index=models.Index(fields=['company', 'date'], name='core_companyusagedaily_company_date_idx'),
        ),
    ]
