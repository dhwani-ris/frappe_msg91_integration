import frappe
import pyotp
from frappe.utils.background_jobs import enqueue
from frappe_msg91_integration.msg91_integration.utils import send_otp


def send_token_via_sms_override(otpsecret, token=None, phone_no=None):
    """
    Override send_token_via_sms to use MSG91 OTP service
    
    :param otpsecret: OTP secret for generating HOTP
    :param token: Token to use for HOTP generation
    :param phone_no: Phone number to send OTP to
    """
    if not phone_no:
        return False
    
    try:
        # Generate OTP using HOTP
        hotp = pyotp.HOTP(otpsecret)
        otp_code = hotp.at(int(token))
        
        # Enqueue the MSG91 OTP sending
        enqueue(
            method=send_msg91_otp,
            queue="short",
            timeout=300,
            event=None,
            is_async=True,
            job_name=None,
            now=False,
            phone_no=phone_no,
            otp_code=str(otp_code)
        )
        
        return True
        
    except Exception as e:
        frappe.log_error(
            message=f"Failed to send OTP via MSG91: {str(e)}",
            title="MSG91 2FA OTP Error"
        )
        return False


def send_msg91_otp(phone_no, otp_code):
    """
    Send OTP using MSG91 service
    
    :param phone_no: Phone number to send OTP to
    :param otp_code: OTP code to send
    """
    try:
        result = send_otp(
            number=phone_no,
            otp_length=len(otp_code),
            otp_expiry=5,  # 5 minutes expiry
            otp=otp_code
        )
        
        if not result.get("success"):
            frappe.log_error(
                message=f"MSG91 OTP sending failed: {result.get('error', 'Unknown error')}",
                title="MSG91 2FA OTP Error"
            )
            
    except Exception as e:
        frappe.log_error(
            message=f"Exception in send_msg91_otp: {str(e)}",
            title="MSG91 2FA OTP Error"
        )


def apply_twofactor_override():
    """Apply the override for send_token_via_sms function"""
    import frappe.twofactor
    
    # Override the function
    frappe.twofactor.send_token_via_sms = send_token_via_sms_override 