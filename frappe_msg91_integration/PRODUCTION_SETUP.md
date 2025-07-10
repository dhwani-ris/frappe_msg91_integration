# MSG91 Integration - Production Setup Guide

## Quick Setup Checklist

### 1. Installation
```bash
bench get-app https://github.com/your-repo/frappe_msg91_integration
bench install-app frappe_msg91_integration
bench restart && bench migrate
```

### 2. MSG91 Configuration
1. Login to your MSG91 account
2. Get your Auth Key from API settings
3. Create/verify your Sender ID
4. Note your template IDs if using templates

### 3. Frappe Configuration
Navigate to **MSG91 Settings**:
```
✓ Enable Integration: Checked
✓ Auth Key: [Your MSG91 Auth Key]
✓ Sender ID: [6-character approved sender ID]
✓ Two Factor Authentication Message: "Your login code is {otp}. Valid for 5 minutes."
```

### 4. Two-Factor Authentication Setup
1. Go to **System Settings**
2. Enable "Two Factor Authentication"
3. Set "Two Factor Method" to "SMS"
4. Configure roles that require 2FA in **Role** doctype

### 5. Verification
- Test 2FA login with a user who has a mobile number
- Check that SMS is sent via MSG91 (not Frappe's SMS Settings)
- Verify OTP functionality works correctly

## Environment-Specific Settings

### Development
```python
# In site_config.json
{
    "msg91_debug_mode": true,
    "msg91_test_mobile": "919999999999"
}
```

### Production
```python
# In site_config.json  
{
    "msg91_rate_limit": true,
    "msg91_monitor_usage": true
}
```

## Security Best Practices

1. **Secure Credentials**: MSG91 Auth Key is encrypted in database
2. **Rate Limiting**: Built-in rate limiting on OTP endpoints
3. **Mobile Validation**: Ensure proper mobile number validation
4. **Monitor Usage**: Track SMS costs and delivery rates
5. **Backup SMS**: Keep Frappe SMS Settings as fallback

## Monitoring & Maintenance

### Daily Checks
- Monitor SMS delivery rates in MSG91 dashboard
- Check Frappe error logs for failed SMS
- Verify 2FA is working for users

### Weekly Reviews
- Review SMS usage and costs
- Check for any failed authentications
- Update mobile numbers for users as needed

### Monthly Tasks
- Review MSG91 account balance
- Audit 2FA-enabled users
- Update templates if needed

## Common Production Issues

### Issue: High SMS Costs
**Solution**: 
- Review message templates for length
- Check for unnecessary SMS sends
- Implement usage alerts

### Issue: 2FA Failures
**Solution**:
- Verify user mobile numbers are correct
- Check MSG91 sender ID status
- Review delivery reports in MSG91

### Issue: Performance Impact
**Solution**:
- SMS sending is asynchronous by default
- Monitor server resources during peak usage
- Consider SMS queuing for high volume

## Support Escalation

1. **App Issues**: Check GitHub issues and documentation
2. **MSG91 API Issues**: Contact MSG91 support with API logs
3. **Frappe Integration**: Check Frappe community forums

## Backup & Recovery

- **Settings Backup**: Include MSG91 Settings in regular site backups
- **Fallback SMS**: Keep Frappe SMS Settings configured as backup
- **Template Backup**: Document all MSG91 templates used

---

**Production Deployment Status**: ✅ Ready for production use with proper monitoring 