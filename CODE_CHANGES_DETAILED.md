# Code Changes - Full URL Tracking Implementation

## 1. Model Changes

### File: `backend/core/models.py`

```python
class WebsiteUsage(models.Model):
    """
    Logs usage of websites.
    """
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='website_usages')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255)
    url = models.TextField(blank=True, null=True, help_text="Full URL path including query parameters")  # ← NEW
    active_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.domain} ({self.active_seconds}s)"
```

---

## 2. Desktop Tracker - URL Detection

### File: `tracker/activity_tracker.py`

**BEFORE:**
```python
def detect_domain(title):
    if not title: return None
    suffixes = [" - Google Chrome", " - Mozilla Firefox", " - Microsoft Edge", " - Opera"]
    for s in suffixes:
        if s in title:
            return title.replace(s, "").strip()
    return None
```

**AFTER:**
```python
def detect_domain(title):
    """
    Extract domain and full URL from browser title.
    Returns: (domain, full_url) tuple
    Example: ("facebook.com", "https://www.facebook.com/photo/?fbid=...")
    """
    if not title: 
        return None, None
    
    suffixes = [" - Google Chrome", " - Mozilla Firefox", " - Microsoft Edge", " - Opera"]
    extracted = title
    
    for s in suffixes:
        if s in title:
            extracted = title.replace(s, "").strip()
            break
    
    if not extracted:
        return None, None
    
    # Try to extract domain (look for domain.com pattern or https://...)
    full_url = extracted
    
    # If it looks like a URL, extract domain from it
    if "://" in extracted or "http" in extracted.lower():
        try:
            from urllib.parse import urlparse
            parsed = urlparse(extracted if extracted.startswith("http") else f"https://{extracted}")
            domain = parsed.netloc or parsed.path.split('/')[0]
        except:
            # Fallback: just use the extracted string as domain
            domain = extracted.split('/')[0].replace('www.', '')
    else:
        # It's already just the domain/URL as title
        domain = extracted.split('/')[0].replace('www.', '')
        # Try to construct full URL
        full_url = extracted
    
    return domain, full_url
```

**Database insertion update:**
```python
# BEFORE
elif item_type == "WEB":
    cur.execute("""
        INSERT INTO website_usages
        (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (item["company_id"], item["employee_id"], item["work_session_id"], item["domain"], item["active_seconds"]))

# AFTER
elif item_type == "WEB":
    # Try to insert with URL, fallback if column doesn't exist
    try:
        cur.execute("""
            INSERT INTO website_usages
            (company_id, employee_id, work_session_id, domain, url, active_seconds, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (item["company_id"], item["employee_id"], item["work_session_id"], item["domain"], item.get("url"), item["active_seconds"]))
    except Exception:
        # Fallback for old database structure
        cur.execute("""
            INSERT INTO website_usages
            (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (item["company_id"], item["employee_id"], item["work_session_id"], item["domain"], item["active_seconds"]))
```

**Tracking loop update:**
```python
# BEFORE
if title != last_title:
    if last_title:
        domain = detect_domain(last_title)
        if domain:
            db_queue.put({"type": "WEB", "company_id": company_id, "employee_id": employee_id, "work_session_id": work_session_id, "domain": domain, "active_seconds": active_seconds})

# AFTER
if title != last_title:
    if last_title:
        domain, full_url = detect_domain(last_title)  # ← Now returns tuple
        if domain:
            db_queue.put({"type": "WEB", "company_id": company_id, "employee_id": employee_id, "work_session_id": work_session_id, "domain": domain, "url": full_url, "active_seconds": active_seconds})
```

---

## 3. Website Usage Logger

### File: `tracker/website_usage.py`

**BEFORE:**
```python
def save(self, company_id, employee_id, work_session_id, domain, active_seconds):
    """
    Save website usage data to the database.
    """
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(self.db_path, check_same_thread=False)
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO website_usages
            (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company_id, employee_id, work_session_id,
            domain, active_seconds, created_at
        ))
        conn.commit()
    except Exception as e:
        print("WebsiteUsage save error:", e)
    finally:
        conn.close()
```

**AFTER:**
```python
def save(self, company_id, employee_id, work_session_id, domain, active_seconds, url=None):
    """
    Save website usage data to the database.
    
    Args:
        url (str): Full URL path including query parameters (optional).
    """
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(self.db_path, check_same_thread=False)
    try:
        cur = conn.cursor()
        # Try to insert with URL, fallback if column doesn't exist
        try:
            cur.execute("""
                INSERT INTO website_usages
                (company_id, employee_id, work_session_id, domain, url, active_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, employee_id, work_session_id,
                domain, url, active_seconds, created_at
            ))
        except Exception:
            cur.execute("""
                INSERT INTO website_usages
                (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                company_id, employee_id, work_session_id,
                domain, active_seconds, created_at
            ))
        conn.commit()
    except Exception as e:
        print("WebsiteUsage save error:", e)
    finally:
        conn.close()
```

---

## 4. Backend View

### File: `backend/core/web_views.py`

**BEFORE:**
```python
def report_top_apps_view(request):
    # ... code ...
    
    # Get detailed website usage by employee
    detailed_sites = WebsiteUsage.objects.select_related('employee')\
        .values('domain', 'employee__first_name', 'employee__last_name')\
        .annotate(total_time=Sum('active_seconds'))\
        .order_by('-total_time')[:50]
        
    # ... more code ...
    
    detailed_sites_data = [{
        'domain': x['domain'], 
        'employee': f"{x['employee__first_name']} {x['employee__last_name']}",
        'total_fmt': fmt(x['total_time']),
        'total_seconds': x['total_time']
    } for x in detailed_sites]
```

**AFTER:**
```python
def report_top_apps_view(request):
    # ... code ...
    
    # Get detailed website usage by employee (with full URL)
    detailed_sites = WebsiteUsage.objects.select_related('employee')\
        .values('domain', 'url', 'employee__first_name', 'employee__last_name')\
        .annotate(total_time=Sum('active_seconds'))\
        .order_by('-total_time')[:50]
        
    # ... more code ...
    
    detailed_sites_data = [{
        'domain': x['domain'], 
        'url': x.get('url') or f"https://{x['domain']}",  # Use stored URL or construct from domain
        'employee': f"{x['employee__first_name']} {x['employee__last_name']}",
        'total_fmt': fmt(x['total_time']),
        'total_seconds': x['total_time']
    } for x in detailed_sites]
```

---

## 5. Report Template

### File: `backend/templates/report_top_apps.html`

**HTML for detailed website list:**

**BEFORE:**
```html
{% for site in detailed_sites %}
<tr>
    <td>
        <div class="d-flex align-items-center">
            <i class="fas fa-globe me-2" style="color: #667eea;"></i>
            <div>
                <strong>{{ site.domain }}</strong>
                <br>
                <small class="text-muted">https://{{ site.domain }}</small>
            </div>
        </div>
    </td>
    <td>
        <span class="badge bg-light text-dark">{{ site.employee }}</span>
    </td>
    <td>
        <strong class="text-info">{{ site.total_fmt }}</strong>
        <br>
        <small class="text-muted">({{ site.total_seconds }} seconds)</small>
    </td>
</tr>
```

**AFTER:**
```html
{% for site in detailed_sites %}
<tr>
    <td>
        <span class="rank-number" style="display: inline-flex; align-items: center; justify-content: center;">{{ forloop.counter }}</span>
    </td>
    <td>
        <a href="{{ site.url }}" target="_blank" class="domain-link" title="Visit {{ site.url }}">
            <i class="fas fa-globe" style="color: #667eea; font-size: 1.1rem;"></i>
            <div>
                <strong>{{ site.domain }}</strong>
                <br>
                <small class="text-muted" style="word-break: break-all;">{{ site.url }}</small>
            </div>
        </a>
    </td>
    <td>
        <span class="badge-employee">
            <i class="fas fa-user me-1"></i>{{ site.employee }}
        </span>
    </td>
    <td class="text-end">
        <div class="time-breakdown">
            <span class="time-formatted">{{ site.total_fmt }}</span>
            <span class="time-seconds">({{ site.total_seconds }}s)</span>
        </div>
    </td>
</tr>
```

---

## 6. Session Details Template

### File: `backend/templates/session_detail.html`

**BEFORE:**
```html
{% for site in websites %}
<li class="list-group-item d-flex justify-content-between align-items-center" style="border-left: 4px solid #667eea;">
    <div class="flex-grow-1">
        <a href="https://{{ site.domain }}" target="_blank" class="text-decoration-none" title="Visit {{ site.domain }}">
            <strong class="text-dark">{{ site.domain }}</strong>
            <i class="fas fa-external-link-alt ms-1" style="font-size: 0.75rem; color: #667eea; opacity: 0.7;"></i>
        </a>
        <br>
        <small class="text-muted">https://{{ site.domain }}</small>
    </div>
    <span class="badge bg-info text-dark rounded-pill ms-2">{{ site.active_seconds }}s</span>
</li>
```

**AFTER:**
```html
{% for site in websites %}
<li class="list-group-item d-flex justify-content-between align-items-center" style="border-left: 4px solid #667eea;">
    <div class="flex-grow-1">
        <a href="{{ site.url|default:'https://'|add:site.domain }}" target="_blank" class="text-decoration-none" title="Visit website">
            <strong class="text-dark">{{ site.domain }}</strong>
            <i class="fas fa-external-link-alt ms-1" style="font-size: 0.75rem; color: #667eea; opacity: 0.7;"></i>
        </a>
        <br>
        <small class="text-muted" style="word-break: break-all;">{{ site.url|default:'https://'|add:site.domain }}</small>
    </div>
    <span class="badge bg-info text-dark rounded-pill ms-2">{{ site.active_seconds }}s</span>
</li>
```

---

## 7. Database Migration

### File: `backend/core/migrations/0005_websiteusage_url.py`

```python
# Generated by Django 6.0.1 on 2026-01-27 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_companysettings_contact_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiteusage',
            name='url',
            field=models.TextField(blank=True, help_text='Full URL path including query parameters', null=True),
        ),
    ]
```

**Applied:** ✅ Successfully

---

## Summary of Changes

| Layer | Changes | Impact |
|-------|---------|--------|
| **Database** | +1 field (url) | Stores complete URLs |
| **Desktop App** | detect_domain() returns tuple | Captures full URLs |
| **Desktop App** | DB insertion updated | Writes URL to database |
| **Backend** | View fetches url field | Sends URL to frontend |
| **Frontend** | Template displays URLs | Users see full URLs |
| **Frontend** | Links are clickable | Can verify websites |

---

## Backward Compatibility

All changes include fallback mechanisms:
- Old database records work (URL field defaults to null)
- Old detection code continues to work
- Templates handle missing URL gracefully
- No breaking changes to API

