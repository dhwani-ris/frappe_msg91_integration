import frappe

def sms_settings_validate(doc, method):
    """Display a warning if SMS Settings is being used but MSG91 is enabled"""
    msg91_settings = frappe.get_single("MSG91 Settings")
    
    if msg91_settings.enabled:
        frappe.msgprint(
            msg="Note: MSG91 Integration is currently enabled. SMS will be sent using MSG91 instead of the configured SMS Settings.",
            title="MSG91 Integration Active",
            indicator="orange"
        ) 