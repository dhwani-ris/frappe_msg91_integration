// MSG91 Integration client-side utilities

// Global namespace for MSG91 Integration
frappe.provide("frappe.msg91");

// SMS sending utility
frappe.msg91.send_sms = function(mobile, message, template, variables, callback) {
    frappe.call({
        method: "frappe_msg91_integration.msg91_integration.api.send_sms_api",
        args: {
            mobile: mobile,
            message: message,
            template: template,
            variables: variables ? JSON.stringify(variables) : null
        },
        callback: function(r) {
            if (callback) callback(r);
        }
    });
};

// OTP sending utility
frappe.msg91.send_otp = function(mobile, otp_length, otp_expiry, callback) {
    frappe.call({
        method: "frappe_msg91_integration.msg91_integration.api.send_otp_api",
        args: {
            mobile: mobile,
            otp_length: otp_length || 4,
            otp_expiry: otp_expiry || 5
        },
        callback: function(r) {
            if (callback) callback(r);
        }
    });
};

// OTP verification utility
frappe.msg91.verify_otp = function(mobile, otp, callback) {
    frappe.call({
        method: "frappe_msg91_integration.msg91_integration.api.verify_otp_api",
        args: {
            mobile: mobile,
            otp: otp
        },
        callback: function(r) {
            if (callback) callback(r);
        }
    });
};

// OTP resend utility
frappe.msg91.resend_otp = function(mobile, retrytype, callback) {
    frappe.call({
        method: "frappe_msg91_integration.msg91_integration.api.resend_otp_api",
        args: {
            mobile: mobile,
            retrytype: retrytype || "text"
        },
        callback: function(r) {
            if (callback) callback(r);
        }
    });
}; 