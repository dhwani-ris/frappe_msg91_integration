# MSG91 Integration

This app provides integration with the MSG91 SMS gateway for Frappe Framework. It allows you to configure and use MSG91 for sending both transactional and promotional SMS messages, as well as comprehensive OTP functionality, overriding the default SMS settings.

## Features

- Configure MSG91 SMS gateway from the UI
- Send transactional SMS using templates
- Send promotional SMS with custom messages 
- Complete OTP functionality:
  - Generate and send OTP
  - Verify OTP codes
  - Resend OTP via text/voice
- REST API endpoints for all SMS and OTP operations
- Client-side JavaScript utilities for easy integration

## Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO
bench install-app frappe_msg91_integration
```

After installation, a default MSG91 Settings document will be created. You'll need to configure it with your MSG91 credentials.

## Configuration

1. Go to **MSG91 Integration > MSG91 Settings**
2. Enter your MSG91 Auth Key and Sender ID (6 characters)
3. Check the "Enabled" checkbox to activate MSG91 integration
4. for OTP Template template name should be otp_template_id
5. Save the settings

## Usage

### Sending SMS

Once configured, any SMS sent using Frappe's standard `frappe.core.doctype.sms_settings.sms_settings.send_sms` method will automatically use MSG91 instead.

```python
from frappe.core.doctype.sms_settings.sms_settings import send_sms

# This will use MSG91 if enabled
send_sms(['9999999999'], 'Your message here')
```

You can also use the MSG91 utilities directly:

```python
from frappe_msg91_integration.msg91_integration.utils import send_sms

# Send SMS directly using MSG91
send_sms(
    number='9999999999',
    message='Your message here'
)

# Using a template from MSG91 Settings
send_sms(
    number='9999999999',
    template_name='welcome',
    variables={'var1': 'John', 'var2': 'ACME'}
)
```

### OTP Functions

```python
from frappe_msg91_integration.msg91_integration.utils import send_otp, verify_otp, resend_otp

# Send OTP
send_otp('9999999999')

# Verify OTP
result = verify_otp('9999999999', '1234')
if result['success']:
    # OTP verified successfully
    pass

# Resend OTP
resend_otp('9999999999')
```

### Client-side JavaScript

```javascript
// Send SMS
frappe.msg91.send_sms('9999999999', 'Your message here', null, null, function(response) {
    console.log(response);
});

// Send SMS with template
frappe.msg91.send_sms('9999999999', null, 'welcome', {name: 'John', company: 'ACME'}, function(response) {
    console.log(response);
});

// Send OTP
frappe.msg91.send_otp('9999999999', null, 4, 5, function(response) {
    console.log(response);
});

// Verify OTP
frappe.msg91.verify_otp('9999999999', '1234', function(response) {
    console.log(response);
});

// Resend OTP
frappe.msg91.resend_otp('9999999999', 'text', function(response) {
    console.log(response);
});
```

### REST API Endpoints

These endpoints can be accessed via HTTP requests to your Frappe server:

- **Send SMS**: `POST /api/method/frappe_msg91_integration.msg91_integration.api.send_sms_api`
  - Parameters: `mobile`, `message`, `template` (optional), `variables` (optional JSON string)

- **Send OTP**: `POST /api/method/frappe_msg91_integration.msg91_integration.api.send_otp_api`
  - Parameters: `mobile`, `template_id` (optional), `otp_length` (optional), `otp_expiry` (optional)

- **Verify OTP**: `POST /api/method/frappe_msg91_integration.msg91_integration.api.verify_otp_api`
  - Parameters: `mobile`, `otp`

- **Resend OTP**: `POST /api/method/frappe_msg91_integration.msg91_integration.api.resend_otp_api`
  - Parameters: `mobile`, `retrytype` (optional, default: "text")

## Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/frappe_msg91_integration
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

## License

MIT
