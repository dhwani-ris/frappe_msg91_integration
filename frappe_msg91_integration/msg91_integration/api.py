import frappe
from frappe import _
from frappe.utils.password import get_decrypted_password
from frappe import _
from frappe.utils import cstr
import json
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

@frappe.whitelist()
def send_otp_api(mobile, otp_length=4, otp_expiry=5):
    """API endpoint to send OTP"""
    result = send_otp(
        number=mobile,
        otp_length=int(otp_length),
        otp_expiry=int(otp_expiry)
    )
    
    return result

@frappe.whitelist()
def verify_otp_api(mobile, otp):
    """API endpoint to verify OTP"""
    result = verify_otp(
        number=mobile,
        otp=otp
    )
    
    return result

@frappe.whitelist(allow_guest=True)
def resend_otp_api(mobile, retrytype="text"):
    """API endpoint to resend OTP"""
    result = resend_otp(
        number=mobile,
        retrytype=retrytype
    )
    
    return result 