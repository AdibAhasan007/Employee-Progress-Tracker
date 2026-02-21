import requests
import json
import time
from datetime import datetime
from pathlib import Path
import config
from api_helper import api_get


class ConfigManager:
    """
    Manages realtime configuration sync from backend API.
    Desktop app polls API at regular intervals to fetch updated policy.
    Applies changes immediately without requiring app restart.
    """
    
    def __init__(self):
        """Initialize config manager with defaults"""
        self.config_file = Path(config.APP_ROOT) / "config_cache.json"
        self.local_config = self._load_from_cache()
        self.api_config = None
        self.last_check_time = 0
        self.config_version = self.local_config.get('config_version', 0)
        self.last_update_time = self.local_config.get('updated_at', None)
        
        self._log("🔧 ConfigManager initialized")

    def _log(self, message: str):
        if config.DEBUG_LOGS:
            print(message)
    
    def get_config(self):
        """Get current active configuration (prefers API, falls back to cache)"""
        return self.api_config or self.local_config
    
    def _load_from_cache(self):
        """Load configuration from local cache file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self._get_default_config()
        return self._get_default_config()
    
    def _save_to_cache(self, config_data):
        """Save configuration to local cache file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            self._log(f"✅ Config cached: v{config_data.get('config_version', 0)}")
        except Exception as e:
            self._log(f"❌ Cache save error: {e}")
    
    def _get_default_config(self):
        """Return default configuration values"""
        return {
            'screenshots_enabled': True,
            'website_tracking_enabled': True,
            'app_tracking_enabled': True,
            'screenshot_interval_seconds': 600,
            'idle_threshold_seconds': 300,
            'config_sync_interval_seconds': 10,
            'max_screenshot_size_mb': 5,
            'screenshot_quality': 85,
            'enable_keyboard_tracking': False,
            'enable_mouse_tracking': False,
            'enable_idle_detection': True,
            'show_tracker_notification': True,
            'notification_interval_minutes': 30,
            'local_data_retention_days': 30,
            'config_version': 1,
            'updated_at': datetime.now().isoformat(),
        }
    
    def check_for_updates(self, employee_token):
        """
        Check if config has been updated on server.
        Call this every N seconds from main app.
        
        Args:
            employee_token: Employee authentication token
        
        Returns:
            True if config was updated, False otherwise
        """
        current_time = time.time()
        
        # Only check at specified interval
        check_interval = self.get_config().get('config_sync_interval_seconds', 10)
        if current_time - self.last_check_time < check_interval:
            return False
        
        self.last_check_time = current_time
        return self._fetch_from_api(employee_token)
    
    def _fetch_from_api(self, employee_token):
        """
        Fetch configuration from backend API.
        
        Returns:
            True if config was updated, False otherwise
        """
        try:
            response = api_get("/employee-config/", token=employee_token, timeout=5)
            
            if response.status_code == 401:
                self._log("❌ Auth failed - token invalid")
                return False
            
            if response.status_code != 200:
                self._log(f"⚠️  API error: {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get('status'):
                self._log(f"❌ Config fetch failed: {data.get('message', 'Unknown error')}")
                return False
            
            # Extract config from response
            new_config = data.get('config', {})
            new_version = new_config.get('config_version', 0)
            
            # Check if version changed
            if new_version <= self.config_version:
                # Config not changed
                return False
            
            # Config changed! Apply new configuration
            self._log(f"🔄 Config update: v{self.config_version} → v{new_version}")
            self._apply_config(new_config)
            
            return True
        
        except requests.exceptions.Timeout:
            self._log("⏱️  Config check timeout")
            return False
        except requests.exceptions.ConnectionError:
            self._log("🔌 Network error - using cached config")
            return False
        except Exception as e:
            self._log(f"❌ Config fetch error: {e}")
            return False
    
    def _apply_config(self, new_config):
        """
        Apply new configuration and notify app.
        
        Args:
            new_config: New config dict from API
        """
        try:
            # Update instance variables
            old_version = self.config_version
            self.api_config = new_config
            self.config_version = new_config.get('config_version', 0)
            self.last_update_time = new_config.get('updated_at', datetime.now().isoformat())
            
            # Save to cache for offline use
            self._save_to_cache(new_config)
            
            # Notify user of changes
            changed_fields = self._get_changed_fields(new_config)
            if changed_fields:
                self._show_notification(changed_fields)
            
            self._log(f"✅ Config applied: {len(changed_fields)} changes")
        
        except Exception as e:
            self._log(f"❌ Config apply error: {e}")
    
    def _get_changed_fields(self, new_config):
        """Get list of fields that changed"""
        old_config = self.local_config or self._get_default_config()
        changed = []
        
        for key in new_config:
            if key == 'updated_at':
                continue
            old_value = old_config.get(key)
            new_value = new_config.get(key)
            if old_value != new_value:
                changed.append({
                    'field': key,
                    'old': old_value,
                    'new': new_value,
                })
        
        return changed
    
    def _show_notification(self, changed_fields):
        """Show system notification about config changes"""
        if not self.get_config().get('show_tracker_notification', True):
            return
        
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            message = "🔄 Configuration Updated\n\n"
            for item in changed_fields[:5]:  # Show first 5 changes
                message += f"• {item['field']}\n"
            
            if len(changed_fields) > 5:
                message += f"\n+ {len(changed_fields) - 5} more changes"
            
            # Try to show notification
            # This is best-effort - may not work depending on context
            self._log(f"📢 Notification: Config updated with {len(changed_fields)} changes")
        
        except Exception as e:
            self._log(f"Notification error: {e}")
    
    def get_setting(self, setting_name, default=None):
        """
        Get individual setting value.
        
        Args:
            setting_name: Name of the setting
            default: Default value if not found
        
        Returns:
            Setting value
        """
        config_data = self.get_config()
        return config_data.get(setting_name, default)
    
    def update_setting(self, setting_name, value):
        """
        Update local setting (doesn't sync back to server).
        Use for app-specific overrides only.
        
        Args:
            setting_name: Name of setting
            value: New value
        """
        if self.api_config:
            self.api_config[setting_name] = value
        else:
            self.local_config[setting_name] = value
        
        self._log(f"⚙️  Setting updated: {setting_name} = {value}")
    
    def force_refresh(self, employee_token):
        """Force immediate config refresh from API"""
        self._log("🔄 Forcing config refresh...")
        self.last_check_time = 0  # Reset timer
        return self._fetch_from_api(employee_token)
    
    def get_status_info(self):
        """Get human-readable config status"""
        config_data = self.get_config()
        return {
            'version': config_data.get('config_version', 0),
            'last_update': config_data.get('updated_at', 'Never'),
            'screenshot_interval': f"{config_data.get('screenshot_interval_seconds', 600)}s",
            'sync_check_interval': f"{config_data.get('config_sync_interval_seconds', 10)}s",
            'features_enabled': sum([
                config_data.get('screenshots_enabled', False),
                config_data.get('website_tracking_enabled', False),
                config_data.get('app_tracking_enabled', False),
            ]),
        }
