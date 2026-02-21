"""
API Helper Module
Centralizes API requests with proper headers (including X-Company-Key)
"""
import requests
import config
from config import API_URL

# Company Key for multi-tenant support
COMPANY_KEY = config.COMPANY_KEY

def get_headers(token=None):
    """
    Get standard headers for API requests
    
    Args:
        token: Optional authentication token
        
    Returns:
        dict: Headers dictionary with X-Company-Key and optional auth
    """
    headers = {
        'X-Company-Key': COMPANY_KEY,
        'Content-Type': 'application/json'
    }
    
    if token:
        headers['Authorization'] = f'Token {token}'
    
    return headers


def _build_url(endpoint: str) -> str:
    if endpoint.startswith("/"):
        return f"{API_URL}{endpoint}"
    return f"{API_URL}/{endpoint}"


def api_post(endpoint, json_data=None, data=None, token=None, timeout=30):
    """
    Make POST request with proper headers
    
    Args:
        endpoint: API endpoint (e.g., '/login')
        json_data: JSON data to send
        data: Form data to send
        token: Optional authentication token
        timeout: Request timeout
        
    Returns:
        Response object
    """
    url = _build_url(endpoint)
    headers = get_headers(token)
    
    if json_data is not None:
        return requests.post(url, json=json_data, headers=headers, timeout=timeout)
    if data is not None:
        return requests.post(url, json=data, headers=headers, timeout=timeout)
    return requests.post(url, headers=headers, timeout=timeout)


def api_get(endpoint, token=None, timeout=5):
    """
    Make GET request with proper headers
    
    Args:
        endpoint: API endpoint
        token: Optional authentication token
        timeout: Request timeout
        
    Returns:
        Response object
    """
    url = _build_url(endpoint)
    headers = get_headers(token)
    
    return requests.get(url, headers=headers, timeout=timeout)
