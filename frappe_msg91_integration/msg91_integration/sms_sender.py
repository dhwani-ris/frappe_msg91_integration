import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms as frappe_send_sms_original
from frappe_msg91_integration.msg91_integration.utils import send_sms

def frappe_send_sms(receiver_list, msg, sender_name="", success_msg=True):
    """Override Frappe's send_sms function to use MSG91 if enabled"""
    try:
        # Check if MSG91 is enabled
        settings = frappe.get_single("MSG91 Settings")
        if settings.enabled:
            # Use MSG91 to send SMS
            response = send_sms(receiver_list=receiver_list, template_name=msg)
            
            if success_msg:
                frappe.msgprint("SMS sent successfully via MSG91")

            return response
    except Exception as e:
        frappe.log_error(f"Failed to send SMS via MSG91: {str(e)}", "MSG91 SMS Error")
        frappe.throw(f"Failed to send SMS via MSG91: {str(e)}")
    
    # If MSG91 is not enabled or there was an error, use default SMS service
    return frappe_send_sms_original(receiver_list, msg, sender_name, success_msg) 