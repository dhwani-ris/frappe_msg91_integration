def apply_monkey_patch():
    """Apply monkey patch with proper error handling"""
    try:
        import frappe
        import frappe.twofactor
        from frappe_msg91_integration.msg91_integration.utils import send_token_via_sms_msg91
        
        # Store original function for reference
        if not hasattr(frappe.twofactor, '_original_send_token_via_sms'):
            frappe.twofactor._original_send_token_via_sms = frappe.twofactor.send_token_via_sms
        
        # Apply the monkey patch
        frappe.twofactor.send_token_via_sms = send_token_via_sms_msg91
        
        frappe.logger().info("MSG91 2FA SMS override applied successfully")
        
    except Exception as e:
        # Log error but don't fail app loading
        try:
            frappe.logger().error(f"Failed to apply MSG91 monkey patch: {str(e)}")
        except:
            pass

# Apply immediately on import
apply_monkey_patch()
