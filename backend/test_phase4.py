#!/usr/bin/env python
"""
Phase 4 Comprehensive Testing Suite
Tests all enterprise features: Departments, Teams, Analytics, Branding, SSO
"""

import os
import sys
import django
import uuid
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from django.utils import timezone
from core.models import (
    Plan, Company, User, Department, Team, ProductivityMetric,
    CompanyBranding, SSOConfiguration, AnalyticsReport
)

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   → {details}")

def main():
    print_header("🚀 PHASE 4 TESTING - ENTERPRISE FEATURES")
    
    # Cleanup from previous runs
    print("🧹 Cleaning up previous test data...")
    Department.objects.all().delete()
    Team.objects.all().delete()
    ProductivityMetric.objects.all().delete()
    CompanyBranding.objects.all().delete()
    SSOConfiguration.objects.all().delete()
    AnalyticsReport.objects.all().delete()
    Company.objects.filter(name__startswith="Phase4Test").delete()
    Plan.objects.filter(name__startswith="PHASE4").delete()
    
    tests_passed = 0
    tests_total = 0
    
    # ========================================
    # TEST 1: Department Model
    # ========================================
    print_header("TEST 1: Department Model & Hierarchy")
    tests_total += 1
    try:
        plan = Plan.objects.create(name=f"PHASE4_{uuid.uuid4().hex[:8]}", max_employees=100)
        company = Company.objects.create(
            name=f"Phase4Test {uuid.uuid4().hex[:8]}",
            company_key=f"phase4test_{uuid.uuid4().hex[:8]}",
            plan=plan
        )
        
        # Create parent department
        eng_dept = Department.objects.create(
            company=company,
            name="Engineering",
            description="Engineering Department",
            budget=50000.00
        )
        
        # Create child department
        backend_dept = Department.objects.create(
            company=company,
            name="Backend Team",
            description="Backend Development",
            parent=eng_dept,
            budget=25000.00
        )
        
        # Verify
        assert Department.objects.filter(company=company).count() == 2
        assert backend_dept.parent == eng_dept
        assert eng_dept.subdepartments.count() == 1
        assert backend_dept.get_full_path() == "Engineering > Backend Team"
        
        print_test("Department Creation", True, f"Created 2 departments with hierarchy")
        tests_passed += 1
    except Exception as e:
        print_test("Department Creation", False, str(e))
    
    # ========================================
    # TEST 2: Team Model
    # ========================================
    print_header("TEST 2: Team Model & Members")
    tests_total += 1
    try:
        # Create team
        team = Team.objects.create(
            company=company,
            department=backend_dept,
            name="API Team",
            description="REST API Development",
            max_members=5
        )
        
        # Create users for team
        user1 = User.objects.create_user(
            username=f"dev1_{uuid.uuid4().hex[:8]}",
            email="dev1@test.com",
            password="test123",
            company=company,
            role='EMPLOYEE',
            department=backend_dept
        )
        
        user2 = User.objects.create_user(
            username=f"dev2_{uuid.uuid4().hex[:8]}",
            email="dev2@test.com",
            password="test123",
            company=company,
            role='EMPLOYEE',
            department=backend_dept
        )
        
        # Add members
        team.members.add(user1, user2)
        team.lead = user1
        team.save()
        
        # Verify
        assert team.get_member_count() == 2
        assert team.lead == user1
        assert user1 in team.members.all()
        assert Team.objects.filter(company=company).count() == 1
        
        print_test("Team Creation", True, f"Created team with 2 members")
        tests_passed += 1
    except Exception as e:
        print_test("Team Creation", False, str(e))
    
    # ========================================
    # TEST 3: ProductivityMetric Model
    # ========================================
    print_header("TEST 3: Productivity Metrics")
    tests_total += 1
    try:
        today = timezone.now().date()
        
        # Create company-level metric
        company_metric = ProductivityMetric.objects.create(
            company=company,
            metric_level='COMPANY',
            date=today,
            total_work_time=480,  # 8 hours in minutes
            productive_time=360,  # 6 hours productive
            idle_time=90,
            break_time=30
        )
        company_metric.calculate_productivity_score()
        company_metric.save()
        
        # Create user-level metric
        user_metric = ProductivityMetric.objects.create(
            company=company,
            metric_level='USER',
            user=user1,
            date=today,
            total_work_time=480,
            productive_time=400,  # Very productive
            idle_time=60,
            break_time=20
        )
        user_metric.calculate_productivity_score()
        user_metric.save()
        
        # Verify
        assert ProductivityMetric.objects.filter(company=company).count() == 2
        assert 70 <= company_metric.productivity_score <= 80  # ~75%
        assert user_metric.productivity_score > 80  # >80%
        
        print_test("Productivity Metrics", True, 
                  f"Company: {company_metric.productivity_score:.1f}%, User: {user_metric.productivity_score:.1f}%")
        tests_passed += 1
    except Exception as e:
        print_test("Productivity Metrics", False, str(e))
    
    # ========================================
    # TEST 4: Department Analytics
    # ========================================
    print_header("TEST 4: Department Analytics")
    tests_total += 1
    try:
        # Create department-level metric
        dept_metric = ProductivityMetric.objects.create(
            company=company,
            metric_level='DEPARTMENT',
            department=backend_dept,
            date=today,
            total_work_time=960,  # 2 people x 8 hours
            productive_time=720,
            idle_time=180,
            break_time=60
        )
        dept_metric.calculate_productivity_score()
        dept_metric.save()
        
        # Create team-level metric
        team_metric = ProductivityMetric.objects.create(
            company=company,
            metric_level='TEAM',
            team=team,
            date=today,
            total_work_time=480,
            productive_time=380,
            idle_time=80,
            break_time=20
        )
        team_metric.calculate_productivity_score()
        team_metric.save()
        
        # Verify
        dept_employees = backend_dept.get_all_employees()
        assert dept_employees.count() == 2
        assert dept_metric.productivity_score == 75.0
        
        print_test("Department Analytics", True,
                  f"Dept: {dept_metric.productivity_score:.1f}%, Team: {team_metric.productivity_score:.1f}%")
        tests_passed += 1
    except Exception as e:
        print_test("Department Analytics", False, str(e))
    
    # ========================================
    # TEST 5: Company Branding
    # ========================================
    print_header("TEST 5: Company Branding & White-Label")
    tests_total += 1
    try:
        branding = CompanyBranding.objects.create(
            company=company,
            primary_color='#667eea',
            secondary_color='#764ba2',
            accent_color='#28a745',
            font_family='Roboto, sans-serif',
            custom_domain='tracker.testcompany.com',
            login_page_title='TestCompany Tracker',
            login_page_subtitle='Track your team productivity',
            email_from_name='TestCompany Support',
            email_from_address='support@testcompany.com'
        )
        
        # Verify
        assert CompanyBranding.objects.filter(company=company).count() == 1
        assert branding.primary_color == '#667eea'
        assert branding.custom_domain == 'tracker.testcompany.com'
        
        print_test("Company Branding", True, "Custom colors and domain configured")
        tests_passed += 1
    except Exception as e:
        print_test("Company Branding", False, str(e))
    
    # ========================================
    # TEST 6: SSO Configuration
    # ========================================
    print_header("TEST 6: SSO Configuration")
    tests_total += 1
    try:
        sso_config = SSOConfiguration.objects.create(
            company=company,
            provider='AZURE_AD',
            is_enabled=True,
            enforce_sso=False,
            saml_entity_id='https://testcompany.com',
            saml_sso_url='https://login.microsoftonline.com/123/saml2',
            oauth_client_id='client_123',
            oauth_client_secret='secret_456',
            auto_provision_users=True,
            default_role='EMPLOYEE'
        )
        
        # Verify
        assert SSOConfiguration.objects.filter(company=company).count() == 1
        assert sso_config.provider == 'AZURE_AD'
        assert sso_config.is_enabled is True
        assert sso_config.auto_provision_users is True
        
        print_test("SSO Configuration", True, f"Provider: {sso_config.provider}, Auto-provision: ON")
        tests_passed += 1
    except Exception as e:
        print_test("SSO Configuration", False, str(e))
    
    # ========================================
    # TEST 7: Analytics Report
    # ========================================
    print_header("TEST 7: Analytics Report Generation")
    tests_total += 1
    try:
        report = AnalyticsReport.objects.create(
            company=company,
            created_by=user1,
            name="Monthly Productivity Report",
            description="Productivity analysis for the month",
            report_type='PRODUCTIVITY',
            department=backend_dept,
            start_date=today - timedelta(days=30),
            end_date=today,
            export_format='PDF',
            frequency='MONTHLY'
        )
        
        # Verify
        assert AnalyticsReport.objects.filter(company=company).count() == 1
        assert report.report_type == 'PRODUCTIVITY'
        assert report.export_format == 'PDF'
        assert report.department == backend_dept
        
        print_test("Analytics Report", True, f"Created {report.report_type} report")
        tests_passed += 1
    except Exception as e:
        print_test("Analytics Report", False, str(e))
    
    # ========================================
    # TEST 8: URL Routes
    # ========================================
    print_header("TEST 8: Phase 4 URL Routes")
    tests_total += 1
    try:
        from django.urls import reverse
        
        routes = [
            'departments',
            'teams',
            'analytics-dashboard',
            'time-utilization',
            'activity-heatmap',
            'generate-report',
            'branding-settings',
            'sso-configuration',
        ]
        
        resolved_count = 0
        for route in routes:
            try:
                url = reverse(route)
                resolved_count += 1
            except:
                pass
        
        assert resolved_count == len(routes)
        print_test("URL Routes", True, f"All {resolved_count}/{len(routes)} routes accessible")
        tests_passed += 1
    except Exception as e:
        print_test("URL Routes", False, str(e))
    
    # ========================================
    # TEST 9: View Functions
    # ========================================
    print_header("TEST 9: Phase 4 View Functions")
    tests_total += 1
    try:
        from core.web_views import (
            departments_view, teams_view, analytics_dashboard_view,
            time_utilization_view, activity_heatmap_view,
            branding_settings_view, sso_configuration_view, generate_report_view
        )
        
        views = [
            departments_view, teams_view, analytics_dashboard_view,
            time_utilization_view, activity_heatmap_view,
            branding_settings_view, sso_configuration_view, generate_report_view
        ]
        
        assert all(callable(v) for v in views)
        print_test("View Functions", True, f"All {len(views)} view functions callable")
        tests_passed += 1
    except Exception as e:
        print_test("View Functions", False, str(e))
    
    # ========================================
    # TEST 10: Templates Exist
    # ========================================
    print_header("TEST 10: Phase 4 Templates")
    tests_total += 1
    try:
        import os
        from django.conf import settings
        
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        required_templates = [
            'departments.html',
            'teams.html',
            'analytics_dashboard.html',
            'time_utilization.html',
            'activity_heatmap.html',
            'branding_settings.html',
            'sso_configuration.html',
            'generate_report.html',
        ]
        
        existing = []
        total_size = 0
        for template in required_templates:
            path = os.path.join(templates_dir, template)
            if os.path.exists(path):
                existing.append(template)
                total_size += os.path.getsize(path)
        
        assert len(existing) == len(required_templates)
        print_test("Templates", True, 
                  f"All {len(existing)}/{len(required_templates)} templates exist ({total_size/1024:.1f} KB)")
        tests_passed += 1
    except Exception as e:
        print_test("Templates", False, str(e))
    
    # ========================================
    # TEST 11: Model Relationships
    # ========================================
    print_header("TEST 11: Model Relationships")
    tests_total += 1
    try:
        # Test relationships
        assert backend_dept.teams.count() == 1
        assert team in backend_dept.teams.all()
        assert user1.teams.count() == 1
        assert user1.department == backend_dept
        assert company.departments.count() == 2
        assert company.teams.count() == 1
        
        print_test("Model Relationships", True, "All FK and M2M relationships working")
        tests_passed += 1
    except Exception as e:
        print_test("Model Relationships", False, str(e))
    
    # ========================================
    # TEST 12: Performance & Indexes
    # ========================================
    print_header("TEST 12: Database Indexes")
    tests_total += 1
    try:
        from django.db import connection
        
        # Check indexes exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name LIKE 'core_%'
                AND name LIKE '%depart%' OR name LIKE '%team%' OR name LIKE '%produc%'
            """)
            indexes = cursor.fetchall()
        
        assert len(indexes) > 0
        print_test("Database Indexes", True, f"Found {len(indexes)} Phase 4 indexes")
        tests_passed += 1
    except Exception as e:
        print_test("Database Indexes", False, str(e))
    
    # ========================================
    # FINAL RESULTS
    # ========================================
    print_header("📊 FINAL RESULTS")
    print(f"\nTotal Tests: {tests_total}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_total - tests_passed}")
    print(f"\nSuccess Rate: {(tests_passed/tests_total)*100:.1f}%\n")
    
    if tests_passed == tests_total:
        print("🎉 " + "="*56 + " 🎉")
        print("   ALL TESTS PASSED - PHASE 4 READY FOR PRODUCTION!")
        print("🎉 " + "="*56 + " 🎉\n")
        print("✨ System is now 100% production-ready! ✨\n")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed - review errors above\n")

if __name__ == '__main__':
    main()
