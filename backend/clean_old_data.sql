-- Clean old data before multi-tenant migration
DELETE FROM core_screenshot;
DELETE FROM core_applicationusage;
DELETE FROM core_websiteusage;
DELETE FROM core_activitylog;
DELETE FROM core_task;
DELETE FROM core_worksession;
DELETE FROM core_user WHERE role != 'OWNER';
DELETE FROM core_companysettings;
