# MSG91 Integration for Frappe

A production-ready Frappe app that seamlessly integrates MSG91 SMS gateway with Frappe Framework, providing reliable SMS and OTP functionality with automatic Two-Factor Authentication override.

## Features

- **SMS Integration**: Send SMS using MSG91 gateway with template support
- **OTP Services**: Send, verify, and resend OTP with configurable settings
- **2FA Override**: Automatically replaces Frappe's default 2FA SMS with MSG91
- **Fallback Support**: Graceful fallback to Frappe's SMS if MSG91 fails
- **Custom Templates**: Configure custom message templates for 2FA

## Installation

```bash
# Get the app
bench get-app https://github.com/your-repo/frappe_msg91_integration

# Install the app
bench install-app frappe_msg91_integration

# Restart and migrate
bench restart && bench migrate
```

## Configuration

### 1. MSG91 Settings Setup

Navigate to **MSG91 Settings** in your Frappe desk and configure:

- **Enable Integration**: Check the "Enabled" box
- **Auth Key**: Your MSG91 authentication key
- **Sender ID**: 6-character sender ID from MSG91
- **API Routes**: Pre-configured with MSG91 endpoints
- **Templates**: Add your MSG91 SMS templates

### 2. Two-Factor Authentication Message

Set your custom 2FA message template in MSG91 Settings:
```
Your login verification code is {otp}. Valid for 5 minutes. Do not share with anyone.
```

Use `{otp}` as the placeholder for the OTP code.

## Two-Factor Authentication Integration

### Automatic Override System

This app implements a robust three-layer override system:

1. **Import-time Patching**: Applied when the module loads
2. **Boot Session Hook**: Applied during Frappe startup
3. **Function Override**: Direct replacement of SMS functions

### How It Works

1. **Seamless Integration**: Once installed, all 2FA SMS automatically use MSG91
2. **OTP Generation**: Uses Frappe's standard OTP generation mechanism
3. **Custom Messaging**: Applies your configured message template
4. **Error Handling**: Comprehensive logging and fallback mechanisms

### Prerequisites

- Enable Two Factor Authentication in **System Settings**
- Configure user roles that require 2FA in **Role** doctype
- Ensure users have phone/mobile numbers in their profiles

## API Reference

### Core SMS Functions

```python
# Send SMS with template
send_sms(number="919999999999", template_name="welcome", variables={"name": "John"})

# Send SMS with custom message
send_sms(number="919999999999", message="Hello World")

# Send OTP (MSG91 generates OTP)
send_otp(number="919999999999", otp_length=6, otp_expiry=5)

# Send custom OTP
send_otp(number="919999999999", otp="123456")

# Verify OTP
verify_otp(number="919999999999", otp="123456")
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `send_sms_api` | POST | Send SMS with template or message |
| `send_otp_api` | POST | Send OTP (optional custom OTP) |
| `verify_otp_api` | POST | Verify OTP |
| `resend_otp_api` | POST | Resend OTP |

### Example API Usage

```bash
# Send OTP
curl -X POST http://your-site/api/method/frappe_msg91_integration.msg91_integration.api.send_otp_api \
  -H "Content-Type: application/json" \
  -d '{"mobile": "919999999999", "otp_length": 6}'

# Verify OTP
curl -X POST http://your-site/api/method/frappe_msg91_integration.msg91_integration.api.verify_otp_api \
  -H "Content-Type: application/json" \
  -d '{"mobile": "919999999999", "otp": "123456"}'
```

## Production Deployment

### Security Considerations

- Store MSG91 Auth Key securely using Frappe's encryption
- Configure appropriate rate limiting for OTP endpoints
- Monitor SMS usage and costs through MSG91 dashboard
- Implement proper user verification workflows

### Performance

- Asynchronous SMS sending to avoid blocking requests
- Cached settings to minimize database queries
- Efficient error handling and logging

### Monitoring

- Check Frappe error logs for SMS delivery issues
- Monitor MSG91 delivery reports
- Set up alerts for authentication failures

## Troubleshooting

### Common Issues

**2FA still using Frappe SMS:**
- Restart Frappe server to apply overrides
- Check MSG91 Settings are enabled
- Verify MSG91 credentials are correct

**SMS delivery failures:**
- Check MSG91 account balance
- Verify sender ID is approved
- Ensure mobile numbers include country code

**OTP verification failing:**
- Check OTP expiry settings
- Verify mobile number format
- Check MSG91 delivery status

### Debug Information

For troubleshooting, check the following:
- Error logs in Frappe
- MSG91 delivery reports
- Network connectivity to MSG91 APIs

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please use the GitHub issue tracker. 