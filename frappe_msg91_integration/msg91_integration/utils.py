import frappe
import requests
import json
from frappe import _
from frappe.utils.password import get_decrypted_password

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
        "templates": {template.name: template.template_id for template in settings.templates}
    }

def format_mobile_number(number):
    """Format mobile number with country code"""
    if not number:
        return None
    if not str(number).startswith('+'):
        if str(number).startswith('91'):
            number = f"{number}" 
        else:
            number = f"91{number}"
    elif number.startswith('+'):
        number = number[1:]  # Remove the '+' sign
    return number

def send_sms(receiver_list, template_name):
    """
    Send SMS using MSG91
    
    :param number: Mobile number with country code (e.g., 919999999999)
    :param message: Message to send (used if template_name is not provided)
    :param template_name: Name of template configured in MSG91 Settings
    :param variables: Dictionary of variables to use in template
    """
    if not receiver_list:
        frappe.throw(_("Receiver list is required"))
    
    # Format mobile number (ensure it has country code)
    for reciever in receiver_list:
        reciever["mobiles"] = format_mobile_number(reciever.get("mobiles"))
           
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
            "recipients": receiver_list
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

        request_id = str(response.json().get("message"))
        
    
        # Get logs from MSG91
        sms_status = get_logs_from_msg91_with_request_id(request_id)
        # Parse response
        parsed_response = parse_sms_analytics_response(sms_status.get("response").json())
    # Check for success
    if response.status_code >= 200 and response.status_code < 300:
        return {"success": True, "response": parsed_response}
    else:
        frappe.throw(
            message=f"Failed to send SMS: {response.text}",
            title="MSG91 SMS Error"
        )

def get_logs_from_msg91_with_request_id(request_id):
    """
    Get logs from MSG91 with request ID
    
    :param request_id: Request ID
    """
    if not request_id:
        frappe.throw(_("Request ID is required"))
    
    settings = get_msg91_settings()
    
    # Prepare data for OTP
    headers = {
        "authkey": settings["auth_key"],
        "Content-Type": "application/json"
    }

    url = f"https://control.msg91.com/api/v5/report/logs/p/sms?requestId={request_id}"

    # Make API request
    response = requests.post(
        url,
        headers=headers,
    )
    
    # Check for success
    if response.status_code >= 200 and response.status_code < 300:
        return {"success": True, "response": response}
    else:
        frappe.log_error(
            message=f"Failed to get logs: {response.text}",
            title="MSG91 Logs Error"
        )
        return {"success": False, "error": response.text}


def parse_sms_analytics_response(response):
    """
    Parse SMS analytics response
    
    :param response: Response from MSG91
    """
    response_data = []
    for message_object in response.get("data"):
        response_data.append({
            "requestDate": message_object.get("requestDate"),
            "status": message_object.get("status"),
            "deliveryDate": message_object.get("deliveryDate"),
            "deliveryTime": message_object.get("deliveryTime"),
            "sentDateTime": message_object.get("sentDateTime"),
            "telNum": message_object.get("telNum")
        })
    return response_data

def send_otp(number, otp_length=6, otp_expiry=5, otp=None):
    """
    Send OTP using MSG91
    
    :param number: Mobile number with country code
    :param otp_length: Length of OTP (default: 6)
    :param otp_expiry: OTP expiry time in minutes (default: 5)
    :param otp: Optional predefined OTP to send
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
    
    # Add predefined OTP if provided
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