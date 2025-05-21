import frappe
from frappe.model.document import Document
from frappe import _

class MSG91Settings(Document):
    def validate(self):
        if self.enabled:
            if not self.auth_key:
                frappe.throw(_("Auth Key is required when MSG91 is enabled"))
            if not self.sender_id:
                frappe.throw(_("Sender ID is required when MSG91 is enabled"))
            if len(self.sender_id) != 6:
                frappe.throw(_("Sender ID must be exactly 6 characters"))
            
            # Validate API routes
            if not self.otp_route:
                frappe.throw(_("OTP API Route is required"))
            if not self.sms_route:
                frappe.throw(_("SMS API Route is required")) 