import frappe
from frappe import _
from frappe.utils.password import get_decrypted_password
from frappe import _
from frappe.utils import cstr
import json
from frappe.rate_limiter import rate_limit
from frappe_msg91_integration.msg91_integration.utils import send_sms, send_otp, verify_otp, resend_otp

@frappe.whitelist(allow_guest=False)
def get_settings():
    """Get MSG91 settings (for UI consumption)"""
    if not frappe.has_permission("MSG91 Settings", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    settings = frappe.get_single("MSG91 Settings")
    return {
        "enabled": settings.enabled,
        "sender_id": settings.sender_id,
        "otp_route": settings.otp_route,
        "sms_route": settings.sms_route,
        "templates": [{"name": t.template_name, "id": t.template_id} for t in settings.templates]
    }

@frappe.whitelist(allow_guest=False)
def send_sms_api(mobile, message=None, template=None, variables=None):
    """API endpoint to send SMS"""
    if variables and isinstance(variables, str):
        try:
            variables = json.loads(variables)
        except Exception:
            variables = None
    
    result = send_sms(
        number=mobile,
        message=message,
        template_name=template,
        variables=variables
    )
    
    return result

@frappe.whitelist(allow_guest=True,methods=["POST"])
@rate_limit(key='mobile_otp_send', limit=5, seconds=60 * 60)
def send_otp_api(mobile, otp_length=4, otp_expiry=5):
    """API endpoint to send OTP"""
    result = send_otp(
        number=mobile,
        otp_length=int(otp_length),
        otp_expiry=int(otp_expiry)
    )
    
    return result

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key='mobile_otp_verify', limit=5, seconds=60 * 60)
def verify_otp_api(mobile, otp):
    """API endpoint to verify OTP"""
    result = verify_otp(
        number=mobile,
        otp=otp
    )
    
    return result

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key='mobile_otp_send', limit=5, seconds=60 * 60)
def resend_otp_api(mobile, retrytype="text"):
    """API endpoint to resend OTP"""
    result = resend_otp(
        number=mobile,
        retrytype=retrytype
    )
    
    return result

@frappe.whitelist(allow_guest=False)
def check_2fa_override_status():
    """Check if the 2FA SMS override is active"""
    if not frappe.has_permission("MSG91 Settings", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    try:
        import frappe.twofactor
        current_func = getattr(frappe.twofactor, 'send_token_via_sms', None)
        from frappe_msg91_integration.msg91_integration.utils import send_token_via_sms_msg91
        
        is_overridden = current_func == send_token_via_sms_msg91
        
        return {
            "is_overridden": is_overridden,
            "current_function": str(current_func),
            "expected_function": str(send_token_via_sms_msg91),
            "msg91_enabled": frappe.get_single("MSG91 Settings").enabled if frappe.db.exists("Singles", "MSG91 Settings") else False
        }
    except Exception as e:
        return {
            "error": str(e),
            "is_overridden": False
        }

@frappe.whitelist(allow_guest=False)
def force_apply_2fa_override():
    """Manually apply the 2FA SMS override"""
    if not frappe.has_permission("MSG91 Settings", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    try:
        from frappe_msg91_integration.msg91_integration.utils import monkey_patch_twofactor_sms
        monkey_patch_twofactor_sms()
        
        # Check if it worked
        import frappe.twofactor
        current_func = getattr(frappe.twofactor, 'send_token_via_sms', None)
        from frappe_msg91_integration.msg91_integration.utils import send_token_via_sms_msg91
        
        is_overridden = current_func == send_token_via_sms_msg91
        
        return {
            "success": True,
            "is_overridden": is_overridden,
            "message": "Override applied successfully" if is_overridden else "Override may not have been applied correctly"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }