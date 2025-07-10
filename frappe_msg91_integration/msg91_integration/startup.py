import frappe
from frappe_msg91_integration.msg91_integration.utils import monkey_patch_twofactor_sms

def execute():
    """Execute startup tasks for MSG91 integration"""
    monkey_patch_twofactor_sms() 