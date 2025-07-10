# MSG91 Integration - Usage Examples

## Basic SMS Sending

### Simple SMS
```python
from frappe_msg91_integration.msg91_integration.utils import send_sms

# Send simple SMS
result = send_sms(
    number="919999999999",
    message="Hello! This is a test message from your app."
)

if result.get("success"):
    print("SMS sent successfully")
else:
    print(f"SMS failed: {result.get('error')}")
```

### Template-based SMS
```python
# Send SMS using MSG91 template
result = send_sms(
    number="919999999999",
    template_name="welcome_message",
    variables={
        "name": "John Doe",
        "company": "Acme Corp"
    }
)
```

## OTP Functionality

### Send Auto-generated OTP
```python
from frappe_msg91_integration.msg91_integration.utils import send_otp, verify_otp

# MSG91 generates and sends OTP
result = send_otp(
    number="919999999999",
    otp_length=6,
    otp_expiry=5  # 5 minutes
)

if result.get("success"):
    # Store session info for verification
    frappe.session.otp_mobile = "919999999999"
```

### Send Custom OTP
```python
import random

# Generate your own OTP
custom_otp = str(random.randint(100000, 999999))

result = send_otp(
    number="919999999999",
    otp=custom_otp,
    otp_expiry=10
)

# Store OTP in your system for verification
frappe.cache.set(f"custom_otp_{mobile}", custom_otp, 600)
```

### Verify OTP
```python
# Verify OTP
result = verify_otp(
    number="919999999999",
    otp="123456"
)

if result.get("success"):
    print("OTP verified successfully")
    # Proceed with authenticated action
else:
    print("Invalid OTP")
```

## Custom Doctype Integration

### User Registration with OTP
```python
# In your custom doctype controller
import frappe
from frappe_msg91_integration.msg91_integration.utils import send_otp, verify_otp

class CustomerRegistration(Document):
    
    def send_verification_otp(self):
        """Send OTP for mobile verification"""
        if not self.mobile:
            frappe.throw("Mobile number is required")
        
        result = send_otp(
            number=self.mobile,
            otp_length=6,
            otp_expiry=5
        )
        
        if result.get("success"):
            self.db_set("otp_sent_at", frappe.utils.now())
            frappe.msgprint("OTP sent to your mobile number")
        else:
            frappe.throw("Failed to send OTP. Please try again.")
    
    def verify_mobile_otp(self, otp):
        """Verify the OTP and mark mobile as verified"""
        result = verify_otp(
            number=self.mobile,
            otp=otp
        )
        
        if result.get("success"):
            self.db_set("mobile_verified", 1)
            self.db_set("verified_at", frappe.utils.now())
            return True
        else:
            frappe.throw("Invalid OTP. Please try again.")
```

### Custom 2FA Implementation
```python
# For custom apps requiring 2FA
from frappe_msg91_integration.msg91_integration.utils import send_token_via_sms_msg91

def custom_2fa_send_otp(user_mobile, custom_otp):
    """Send custom 2FA OTP"""
    result = send_token_via_sms_msg91(
        phone_no=user_mobile,
        otp=custom_otp
    )
    
    return result
```

## API Integration Examples

### Frontend JavaScript
```javascript
// Send OTP from frontend
frappe.call({
    method: "frappe_msg91_integration.msg91_integration.api.send_otp_api",
    args: {
        mobile: "919999999999",
        otp_length: 6
    },
    callback: function(r) {
        if (r.message.success) {
            frappe.msgprint("OTP sent successfully");
        }
    }
});

// Verify OTP
frappe.call({
    method: "frappe_msg91_integration.msg91_integration.api.verify_otp_api",
    args: {
        mobile: "919999999999",
        otp: "123456"
    },
    callback: function(r) {
        if (r.message.success) {
            frappe.msgprint("Mobile verified successfully");
        }
    }
});
```

### REST API Integration
```python
import requests

# Send OTP via REST API
response = requests.post(
    "https://your-site.com/api/method/frappe_msg91_integration.msg91_integration.api.send_otp_api",
    headers={
        "Authorization": "token your_api_key:your_api_secret",
        "Content-Type": "application/json"
    },
    json={
        "mobile": "919999999999",
        "otp_length": 6
    }
)

result = response.json()
```

## Error Handling

### Robust SMS Sending
```python
def send_sms_with_fallback(mobile, message):
    """Send SMS with proper error handling"""
    try:
        result = send_sms(number=mobile, message=message)
        
        if result.get("success"):
            frappe.logger().info(f"SMS sent successfully to {mobile}")
            return True
        else:
            error_msg = result.get("error", "Unknown error")
            frappe.logger().error(f"SMS failed for {mobile}: {error_msg}")
            
            # Log for admin review
            frappe.log_error(
                message=f"SMS delivery failed: {error_msg}",
                title="MSG91 SMS Failure"
            )
            return False
            
    except Exception as e:
        frappe.logger().error(f"SMS sending exception for {mobile}: {str(e)}")
        return False
```

### OTP Verification with Limits
```python
def verify_otp_with_limits(mobile, otp, max_attempts=3):
    """Verify OTP with attempt limiting"""
    cache_key = f"otp_attempts_{mobile}"
    attempts = frappe.cache.get(cache_key) or 0
    
    if attempts >= max_attempts:
        frappe.throw("Maximum OTP attempts exceeded. Please request a new OTP.")
    
    result = verify_otp(number=mobile, otp=otp)
    
    if result.get("success"):
        # Clear attempts on success
        frappe.cache.delete(cache_key)
        return True
    else:
        # Increment attempts
        frappe.cache.set(cache_key, attempts + 1, 3600)  # 1 hour expiry
        frappe.throw(f"Invalid OTP. {max_attempts - attempts - 1} attempts remaining.")
```

## Best Practices

### Mobile Number Validation
```python
import re

def validate_mobile_number(mobile):
    """Validate mobile number format"""
    # Remove any spaces, dashes, or special characters
    mobile = re.sub(r'[^\d+]', '', mobile)
    
    # Check if it starts with country code
    if mobile.startswith('+91'):
        mobile = mobile[3:]
    elif mobile.startswith('91') and len(mobile) == 12:
        mobile = mobile[2:]
    
    # Validate Indian mobile number (10 digits starting with 6-9)
    if re.match(r'^[6-9]\d{9}$', mobile):
        return f"91{mobile}"
    else:
        frappe.throw("Please enter a valid 10-digit mobile number")
```

### Centralized SMS Configuration
```python
def get_sms_settings():
    """Get centralized SMS configuration"""
    return {
        "default_otp_length": 6,
        "default_otp_expiry": 5,
        "max_daily_sms_per_user": 10,
        "enable_delivery_reports": True
    }
```

This integration is now production-ready with comprehensive error handling, proper validation, and flexible usage patterns! 