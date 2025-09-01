import frappe
import pyotp
from frappe_msg91_integration.msg91_integration.utils import send_otp

def send_token_via_sms(otpsecret, token=None, phone_no=None):
    """
    Generate OTP and send using local send_otp function.
    :param otpsecret: OTP secret for generating HOTP
    :param token: Token to use for HOTP generation
    :param phone_no: Phone number to send OTP to
    """
    if not phone_no:
        return False
    try:
        try:
            token_int = int(token)
        except Exception as conv_exc:
            frappe.log_error(
                message=f"[2FA DEBUG] Could not convert token to int: {token} ({conv_exc})",
                title="MSG91 2FA OTP Debug"
            )
            return False
        hotp = pyotp.HOTP(otpsecret)
        otp_code = hotp.at(token_int)
        result = send_otp(
            number=phone_no,
            otp_length=len(otp_code),
            otp_expiry=5,  # 5 minutes expiry
            otp=otp_code
        )
        return result.get("success", False)
    except Exception as e:
        frappe.log_error(
            message=f"Failed to send OTP via MSG91: {str(e)}",
            title="MSG91 2FA OTP Error"
        )
        return False 