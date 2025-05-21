import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms as frappe_send_sms
from frappe_msg91_integration.msg91_integration.utils import send_sms

def override_frappe_send_sms(receiver_list, msg, sender_name="", success_msg=True):
    """Override Frappe's send_sms function to use MSG91 if enabled"""
    try:
        # Check if MSG91 is enabled
        settings = frappe.get_single("MSG91 Settings")
        if settings.enabled:
            # Use MSG91 to send SMS
            for receiver in receiver_list:
                send_sms(number=receiver, message=msg)
            
            if success_msg:
                frappe.msgprint("SMS sent successfully via MSG91")
            
            return True
    except Exception as e:
        frappe.log_error(f"Failed to send SMS via MSG91: {str(e)}", "MSG91 SMS Error")
    
    # If MSG91 is not enabled or there was an error, use default SMS service
    return frappe_send_sms(receiver_list, msg, sender_name, success_msg) 