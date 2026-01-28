from rest_framework import serializers
from .models import User, WorkSession, ApplicationUsage, WebsiteUsage, ActivityLog, Screenshot, Task, CompanySettings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'tracker_token', 'profile_picture', 'timezone', 'is_active_employee']
        read_only_fields = ['tracker_token']

class WorkSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSession
        fields = '__all__'

class ApplicationUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationUsage
        fields = '__all__'

class WebsiteUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteUsage
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'

class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'

class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = '__all__'
