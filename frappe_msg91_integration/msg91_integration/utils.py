import frappe
import requests
import json
from frappe import _
from frappe.utils.password import get_decrypted_password
import pyotp

def get_msg91_settings():
    """Get MSG91 settings from database"""
    settings = frappe.get_single("MSG91 Settings")
    if not settings.enabled:
        frappe.throw(_("MSG91 integration is not enabled. Please enable it in MSG91 Settings."))
    
    # Return necessary settings
    return {
        "auth_key": get_decrypted_password('MSG91 Settings','MSG91 Settings','auth_key'),
        "sender_id": settings.sender_id,
        "otp_route": settings.otp_route,
        "sms_route": settings.sms_route,
        "templates": {template.template_name: template.template_id for template in settings.templates}
    }

def send_sms(number, message=None, template_name=None, variables=None):
    """
    Send SMS using MSG91
    
    :param number: Mobile number with country code (e.g., 919999999999)
    :param message: Message to send (used if template_name is not provided)
    :param template_name: Name of template configured in MSG91 Settings
    :param variables: Dictionary of variables to use in template
    """
    if not number:
        frappe.throw(_("Mobile number is required"))
    
    # Format mobile number (ensure it has country code)
    if not str(number).startswith('+'):
        if str(number).startswith('91'):
            number = f"{number}" 
        else:
            number = f"91{number}"
    elif number.startswith('+'):
        number = number[1:]  # Remove the '+' sign
    
    settings = get_msg91_settings()
    
    if template_name:
        # Get template ID from settings
        template_id = settings["templates"].get(template_name)
        if not template_id:
            frappe.throw(_("Template '{0}' not found in MSG91 Settings").format(template_name))
        
        # Prepare data for template-based SMS
        data = {
            "flow_id": template_id,
            "sender": settings["sender_id"],
            "recipients": [{"mobiles": number, "VAR": variables or {}}]
        }
        
        # Make API request
        headers = {
            "authkey": settings["auth_key"],
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            settings["sms_route"],
            headers=headers,
            data=json.dumps(data)
        )
    else:
        # Send regular SMS without template
        if not message:
            frappe.throw(_("Either message or template_name must be provided"))
        
        # Prepare data for regular SMS
        data = {
            "sender": settings["sender_id"],
            "route": "4",  # Promotional route
            "country": "91",
            "sms": [{"message": message, "to": [number]}]
        }
        
        # Make API request
        headers = {
            "authkey": settings["auth_key"],
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.msg91.com/api/v2/sendsms",
            headers=headers,
            data=json.dumps(data)
        )
    
    # Check for success
    if response.status_code >= 200 and response.status_code < 300:
        return {"success": True, "response": response.json()}
    else:
        frappe.log_error(
            message=f"Failed to send SMS: {response.text}",
            title="MSG91 SMS Error"
        )
        return {"success": False, "error": response.text}

def send_otp(number, otp=None, otp_length=6, otp_expiry=5):
    """
    Send OTP using MSG91
    
    :param number: Mobile number with country code
    :param otp: Optional specific OTP to send (if not provided, MSG91 will generate one)
    :param otp_length: Length of OTP (default: 6)
    :param otp_expiry: OTP expiry time in minutes (default: 5)
    """
    if not number:
        frappe.throw(_("Mobile number is required"))
    
    # Format mobile number
    if not str(number).startswith('+'):
        if str(number).startswith('91'):
            number = f"{number}" 
        else:
            number = f"91{number}"
    elif number.startswith('+'):
        number = number[1:]  # Remove the '+' sign
    
    settings = get_msg91_settings()
    
    # Prepare data for OTP
    data = {
        "mobile": number,
        "authkey": settings["auth_key"],
        "otp_length": otp_length,
        "otp_expiry": otp_expiry
    }
    
    # Add OTP to request only if provided
    if otp:
        data["otp"] = otp
    
    template_id = settings["templates"].get("otp_template_id")
    if not template_id:
        frappe.throw(_("Template '{0}' not found in MSG91 Settings").format("otp_template_id"))
    
    data["template_id"] = template_id
    # Make API request
    response = requests.post(
        f"{settings['otp_route']}",
        data=data
    )
    
    # Check for success
    if response.status_code >= 200 and response.status_code < 300:
        return {"success": True, "response": response.json()}
    else:
        frappe.log_error(
            message=f"Failed to send OTP: {response.text}",
            title="MSG91 OTP Error"
        )
        return {"success": False, "error": response.text}

def verify_otp(number, otp):
    """
    Verify OTP using MSG91
    
    :param number: Mobile number with country code
    :param otp: OTP to verify
    """
    if not number or not otp:
        frappe.throw(_("Mobile number and OTP are required"))
    
    # Format mobile number
    if not str(number).startswith('+'):
        if str(number).startswith('91'):
            number = f"{number}" 
        else:
            number = f"91{number}"
    elif number.startswith('+'):
        number = number[1:]  # Remove the '+' sign
    
    settings = get_msg91_settings()
    
    # Prepare data for OTP verification
    data = {
        "mobile": number,
        "authkey": settings["auth_key"],
        "otp": otp
    }
    
    # Make API request
    response = requests.post(
        f"{settings['otp_route']}/verify",
        data=data
    )
    
    # Check for success
    if response.status_code >= 200 and response.status_code < 300:
        resp_data = response.json()
        if resp_data.get("type") == "success":
            return {"success": True, "message": "OTP verified successfully"}
        else:
            return {"success": False, "message": resp_data.get("message", "OTP verification failed")}
    else:
        frappe.log_error(
            message=f"Failed to verify OTP: {response.text}",
            title="MSG91 OTP Verification Error"
        )
        return {"success": False, "error": response.text}

def resend_otp(number, retrytype="text"):
    """
    Resend OTP using MSG91
    
    :param number: Mobile number with country code
    :param retrytype: Type of retry - text or voice (default: text)
    """
    if not number:
        frappe.throw(_("Mobile number is required"))
    
    # Format mobile number
    if not str(number).startswith('+'):
        if str(number).startswith('91'):
            number = f"{number}" 
        else:
            number = f"91{number}"
    elif number.startswith('+'):
        number = number[1:]  # Remove the '+' sign
    
    settings = get_msg91_settings()
    
    # Prepare data for OTP resend
    data = {
        "mobile": number,
        "authkey": settings["auth_key"],
        "retrytype": retrytype
    }
    
    # Make API request
    response = requests.post(
        f"{settings['otp_route']}/retry",
        data=data
    )
    
    # Check for success
    if response.status_code >= 200 and response.status_code < 300:
        return {"success": True, "response": response.json()}
    else:
        frappe.log_error(
            message=f"Failed to resend OTP: {response.text}",
            title="MSG91 OTP Resend Error"
        )
        return {"success": False, "error": response.text} 

def send_token_via_sms_msg91(otpsecret, token=None, phone_no=None):
    """
    Override for Frappe's send_token_via_sms function to use MSG91
    
    :param otpsecret: OTP secret from Frappe's 2FA system
    :param token: Token from Frappe's 2FA system
    :param phone_no: Mobile number to send SMS to
    """
    try:
        if not phone_no:
            return False
        
        # Generate OTP using Frappe's method (same as original function)
        hotp = pyotp.HOTP(otpsecret)
        otp = hotp.at(int(token))

        # Send OTP using MSG91
        result = send_otp(
            number=phone_no,
            otp=otp
        )

        if result.get("success"):
            frappe.logger().info(f"2FA SMS sent successfully via MSG91 to {phone_no}")
            return True
        else:
            frappe.log_error(
                message=f"Failed to send 2FA SMS via MSG91: {result.get('error', 'Unknown error')}",
                title="MSG91 2FA SMS Error"
            )
            return False

    except Exception as e:
        frappe.log_error(
            message=f"Error in MSG91 2FA SMS override: {str(e)}",
            title="MSG91 2FA Override Error"
        )


def monkey_patch_twofactor_sms():
    """
    Monkey patch Frappe's send_token_via_sms function to use MSG91
    """
    try:
        import frappe.twofactor
        
        # Store the original function for debugging
        original_func = getattr(frappe.twofactor, 'send_token_via_sms', None)
        
        # Apply the monkey patch
        frappe.twofactor.send_token_via_sms = send_token_via_sms_msg91
        
        # Verify the patch was applied
        current_func = getattr(frappe.twofactor, 'send_token_via_sms', None)
        
        if current_func == send_token_via_sms_msg91:
            frappe.logger().info("MSG91 2FA SMS override successfully applied")
        else:
            frappe.logger().warn("MSG91 2FA SMS override may not have been applied correctly")
            
    except ImportError:
        frappe.logger().warn("Could not import frappe.twofactor for MSG91 override")
    except Exception as e:
                                                                                    frappe.logger().error(f"Error applying MSG91 2FA SMS override: {str(e)}")

def apply_monkey_patch_on_boot(bootinfo=None):
    """
    Apply monkey patch during boot session
    
    :param bootinfo: Boot information passed by Frappe (ignored)
    """
    try:
        # Force import and apply patch
        import frappe.twofactor
        import importlib
        
        # Reload the module to ensure fresh state
        importlib.reload(frappe.twofactor)
        
        # Apply the patch
        frappe.twofactor.send_token_via_sms = send_token_via_sms_msg91
        
        # Also patch the module-level function reference
        import sys
        if 'frappe.twofactor' in sys.modules:
            sys.modules['frappe.twofactor'].send_token_via_sms = send_token_via_sms_msg91
        
        frappe.logger().info("MSG91 2FA SMS override applied via boot session")
        
    except Exception as e:
        frappe.logger().error(f"Error applying MSG91 monkey patch on boot: {str(e)}")

def override_sms_send_request(*args, **kwargs):
    """
    Override frappe.core.doctype.sms_settings.sms_settings.send_request to use MSG91
    This is the function that's being called for 2FA SMS
    """
    try:
        # Check if MSG91 is enabled
        msg91_settings = frappe.get_single("MSG91 Settings")
        if msg91_settings.enabled:
            # Extract parameters from kwargs
            params = kwargs.get('params', {})
            
            # Find phone number and message in params
            phone_no = None
            message = None
            
            for key, value in params.items():
                # Common parameter names for phone numbers
                if key.lower() in ['mobile', 'phone', 'to', 'mobiles', 'mobile_no', 'receiver']:
                    phone_no = value
                # Common parameter names for messages  
                elif key.lower() in ['message', 'msg', 'text', 'sms']:
                    message = value
            
            if phone_no and message:
                frappe.logger().info(f"Intercepting SMS via MSG91 override - Phone: {phone_no}, Message: {message}")
                
                # Use MSG91 to send SMS
                result = send_sms(number=phone_no, message=message)
                frappe.logger().info(f"SMS sent via MSG91 override: {result}")
                return result
    
    except Exception as e:
        frappe.logger().error(f"Error in SMS send_request override: {str(e)}")
    
    # Fall back to original method
    try:
        from frappe.core.doctype.sms_settings.sms_settings import send_request as original_send_request
        return original_send_request(*args, **kwargs)
    except Exception as e:
        frappe.logger().error(f"Error calling original send_request: {str(e)}")
        return False 