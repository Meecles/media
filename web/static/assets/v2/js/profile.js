function init_change_password() {
    let clears = ["current_password", "new_password", "confirm_new_password", "pw_change_alert"];
    for (let i = 0; i < clears.length; i++) {
        $("#" + clears[i]).val("")
    }
    var cancel_btn = "<button class='btn btn-secondary' type='button' data-dismiss='modal'>Cancel</button>";
    var change_btn = "<button type='button' class='btn btn-primary' onClick='change_password()'>Change Password</button>";
    $("#change_password_footer").html(cancel_btn);
    $("#change_password_footer").append(change_btn);
    $("#pw_change_alert").html("");
    $("#changePasswordModal").modal("show");
}

function display_change_error(message) {
    let alert = "<div class='alert alert-danger' role='alert' style='width: 80%;margin-left: auto; margin-right: auto;text-align: center;'>" + message + "</div>"
    $("#pw_change_alert").html(alert)
}

function change_password() {
    let current = $("#current_password").val();
    let new_password = $("#new_password").val();
    let confirm_password = $("#confirm_new_password").val();

    if (new_password !== confirm_password) {
        display_change_error(message)
        return;
    }

    let host_name = ""
    let toSend = {
        "current": current,
        "new": new_password,
        "repeat": confirm_password
    }
    $.ajax({
        url: host_name + "/api/change_password",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify(toSend),
        success: function (data) {
            var success = data.success;
            if (success) {
                var message = "Successfully changed password!"
                var alert = "<div class='alert alert-success' role='alert' style='width: 80%;margin-left: auto; margin-right: auto;text-align: center;'>" + message + "</div>"
                $("#pw_change_alert").html(alert)
                var close_button = "<button class='btn btn-secondary' type='button' data-dismiss='modal'>Close</button>"
                $("#change_password_footer").html(close_button)
            } else {
                display_change_error(data.reason)
            }
        }
    });

}

function logout() {
    window.location.href = "/logout"
}

function init_disable_mfa() {
    $("#disableMfaModal").modal("show");
}

function disable_mfa() {
    var host_name = ""
    var toSend = {}
    $.ajax({
        url: host_name + "/api/mfa/disable",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            var success = data.success;
            if (success) {
                var logout_button = "<button href='/logout' class='btn btn-primary' onClick='logout()'>Logout</button>"
                $("#disable_mfa_footer").html(logout_button)
                $("#mfa-disable-message").html("MFA successfully disabled! Please log out and back in")
            } else {
                $("#mfa-disable-message").html(data.reason)
            }
        }
    });
}

function enable_mfa() {
    var host_name = ""
    var toSend = {
        "token": $("#mfa_token").val()
    }
    $.ajax({
        url: host_name + "/api/mfa/enable",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            var success = data.success;
            if (success) {
                $("#qrcode").html("")
                $("#mfa-input-form").html("")
                var logout_button = "<button href='/logout' class='btn btn-primary' onClick='logout()'>Logout</button>"
                $("#mfa_enable_footer").html(logout_button)
                $("#qr-message").html("MFA successfully enabled! Please log out and back in")
            } else {
                $("#qr-message").html(data.reason)
            }
        }
    });
}

function init_enable_mfa() {
    $("#qrcode").html("")
    $("#qr-message").html("")
    var host_name = ""
    $.ajax({
        url: host_name + "/api/mfa/initiate",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            var success = data.success;
            if (success) {
                let provision_code = data.secret
                new QRCode(document.getElementById("qrcode"), data.provision);
                $("#qr-message").html("Please scan the QR code with google authenticator or authy, then input the code below<br />" +
                    "Alternatively you can enter this code: " + provision_code)
                $("#enableMfaModal").modal("show");
            } else {
                $("#qr-message").html(data.reason)
            }
        }
    });
}
