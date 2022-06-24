let users_role_add = []
let users_list = []
let edit_add_roles = []
let editing_user = null
const _response_message = $("#response-message")

$(document).ready(function () {
    list_users()
})

function goto(loc) {
    window.location.href = loc;
}

function get_user(uid) {
    for (let i = 0; i < users_list.length; i++) {
        if (users_list[i]["id"] === uid)
            return users_list[i]
    }
    return null
}

function get_user_row(uid, username, roles, req, enabled) {
    let role_string = ""
    roles.forEach(function (item) {
        if (item.toLowerCase() === "admin" || item.toLowerCase() === "protected_admin") {
            role_string = role_string + `<span class="badge badge-danger sq">` + item + `</span> `
        } else {
            role_string = role_string + `<span class="badge badge-primary sq">` + item + `</span> `
        }
    })
    let mfa_string = ""
    if (enabled) {
        mfa_string = mfa_string + `<span class="badge badge-success sq">Enabled</span> `
    } else {
        mfa_string = mfa_string + `<span class="badge badge-danger sq">Disabled</span> `
    }
    if (req) {
        mfa_string = mfa_string + `<span class="badge badge-success sq">Required</span> `
    } else {
        mfa_string = mfa_string + `<span class="badge badge-danger sq">Not Required</span> `
    }
    return `<hr class="mgn2" />
            <div class="row mgn">
                <div class="col-3"><p class="txt">` + username + `</p></div>
                <div class="col-5">` + role_string + `</div>
                <div class="col-2">` + mfa_string + `</div>
                <div class="col-2">
                    <button type="button" class="btn btn-outline-dark btn-sm float-right" onclick="open_edit_user('` + uid + `')">Edit</button>
                </div>
            </div>`
}

function get_user_card(uid, username, roles, req, enabled) {
    let role_string = ""
    roles.forEach(function (item) {
        if (item.toLowerCase() === "admin" || item.toLowerCase() === "protected_admin") {
            role_string = role_string + `<span class="badge badge-danger sq">` + item + `</span> `
        } else {
            role_string = role_string + `<span class="badge badge-primary sq">` + item + `</span> `
        }
    })
    let mfa_string = ""
    if (enabled) {
        mfa_string = mfa_string + `<span class="badge badge-success sq">Enabled</span> `
    } else {
        mfa_string = mfa_string + `<span class="badge badge-danger sq">Disabled</span> `
    }
    if (req) {
        mfa_string = mfa_string + `<span class="badge badge-success sq">Required</span> `
    } else {
        mfa_string = mfa_string + `<span class="badge badge-danger sq">Not Required</span> `
    }
    return `<div class="row rw" onclick="open_edit_user('` + uid + `')">
                <div class="col-1"></div>
                <div class="col-10">
                    <div class="card">
                        <div class="card-body">
                            <p><b>Username: &nbsp;</b>` + username + `</p>
                            <p><b>Roles: &nbsp;</b>` + role_string + `</p>
                            <p><b>MFA: &nbsp;</b>` + mfa_string + `</p>
                        </div>
                    </div>
                </div>
                <div class="col-1"></div>
            </div>`
}

function list_users() {
    $.ajax({
        url: "/api/users/list",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data.success;
            if (success) {
                const _users = $("#users")
                const _mobile_users = $("#mobile-users")
                _users.html("")
                _mobile_users.html("")
                users_list = data.users
                data.users.forEach(function (user) {
                    _users.append(get_user_row(user.id, user.username, user.roles,
                        user.mfa_required, user.mfa_enabled))
                    _mobile_users.append(get_user_card(user.id, user.username, user.roles,
                        user.mfa_required, user.mfa_enabled))
                })
            }
        }
    });
}

function open_add_user(mobile) {
    let btn_cancel = `<button class="btn btn-secondary txt-white" type="button" data-dismiss="modal">Cancel</button>`
    let btn_add = `<button type="button" class="btn btn-primary txt-white" onclick="add_user()">Add</button>`
    let footer = $("#add-user-footer")
    $("#new_username").val("")
    $("#role-badges").html("")
    _response_message.html("")
    _response_message.removeClass("text-danger")
    _response_message.removeClass("text-success")
    footer.html(btn_cancel)
    footer.append(btn_add)
    users_role_add = []
    $("#addUserModal").modal("show")
}

function remove_role(role) {
    let values = []
    const _badges = $("#role-badges")
    if (users_role_add.includes(role)) {
        _badges.html("")
        users_role_add.forEach(function (r) {
            if (r !== role) {
                values.push(r)
            }
        })
        users_role_add = values
        users_role_add.forEach(function (r) {
            const role_card = `<div class="alert alert-primary sq" role="alert" style="cursor: pointer;" onclick="remove_role('` + r + `')">`
                + r + `</div>`
            _badges.append(role_card)
        })
    }
}

function add_role(role) {
    if (!users_role_add.includes(role)) {
        users_role_add.push(role)
        const role_card = `<div class="alert alert-primary sq" role="alert" style="cursor: pointer;" onclick="remove_role('` + role + `')">`
            + role + `</div>`
        $("#role-badges").append(role_card)
    }
}

function add_user() {
    const roles = users_role_add
    const username = $("#new_username").val()
    if (roles.length < 1) {
        _response_message.html("Error: You must select at least one role")
        _response_message.addClass("text-danger")
        return;
    }
    if (username.length < 3) {
        _response_message.html("Error: Username must be at least 3 characters")
        _response_message.addClass("text-danger")
        return;
    }
    const toSend = {
        "username": username,
        "roles": roles
    }
    $.ajax({
        url: "/api/users/create",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            _response_message.html("")
            _response_message.removeClass("text-danger")
            _response_message.removeClass("text-success")
            const success = data.success;
            if (success) {
                const pass = data["password"]
                _response_message.html("Success! Password: " + pass)
                _response_message.addClass("text-success")
                let btn_close = `<button class="btn btn-secondary txt-white" type="button" data-dismiss="modal">Close</button>`
                $("#add-user-footer").html(btn_close)
                list_users()
            } else {
                _response_message.html(data["reason"])
                _response_message.addClass("text-danger")
            }
        }
    })
}

function confirm_delete_user(uid) {
    $.ajax({
        url: "/api/users/delete/" + uid,
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            list_users()
            editing_user = null
            $("#deleteUserModal").modal("hide")
        }
    })
}

function delete_user() {
    if (editing_user == null)
        return
    $("#editUserModal").modal("hide")
    run_delete_user(editing_user)
}

function deny_delete_user() {
    $("#deleteUserModal").modal("hide")
    $("#editUserModal").modal("show")
}

function run_delete_user(uid) {
    const btn_no = `<button class="btn btn-secondary txt-white" type="button" onclick="deny_delete_user()">No</button>`
    let btn_yes = `<button type="button" class="btn btn-danger txt-white" onClick="confirm_delete_user('` + uid + `')">Yes</button>`
    let del = $("#delete_user_footer")
    del.html("")
    del.append(btn_no)
    del.append(btn_yes)
    $("#deleteUserModal").modal("show")
}

function edit_user() {
    if (editing_user == null) {
        $("#editUserModal").modal("hide")
        return;
    }
    const username = $("#edit-username").val()
    const mfa_enabled = $("#mfa_enabled").is(":checked")
    const mfa_required = $("#mfa_required").is(":checked")
    let toSend = {
        "id": editing_user,
        "username": username,
        "roles": edit_add_roles,
        "mfa_required": mfa_required
    }
    if (!mfa_enabled) {
        toSend["mfa_enabled"] = false
    }

    $.ajax({
        url: "/api/users/edit",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data["success"]
            console.log(data)
            if (success) {
                $("#editUserModal").modal("hide")
                list_users()
            }
        }
    })
}

function open_edit_user(uid) {
    const user = get_user(uid)
    if (user === null)
        return
    editing_user = uid
    $("#mfa_required").attr("checked", false)
    $("#mfa_enabled").attr("checked", false)
    $("#reset-dialogue").html(`<button class="btn btn-outline-danger txt-danger pull-left" type="button" onclick="reset_pw()">
                Reset Password
                </button>`)
    if (user.mfa_required) {
        $("#mfa_required").attr("checked", true)
    }
    if (user.mfa_enabled) {
        $("#mfa_enabled").attr("checked", true)
        $("#mfa_enabled").prop("disabled", false);
    }
    else {
        $("#mfa_enabled").prop("disabled", true);
    }
    $("#edit-username").val(user.username)
    const _user_roles = $("#user-roles")
    _user_roles.html("")
    user.roles.forEach(function (role) {
        const role_card = `<div class="alert alert-primary sq" role="alert" style="cursor: pointer;" onclick="edit_remove_role('` + role + `')">`
            + role + `</div>`
        edit_add_roles.push(role)
        $("#user-roles").append(role_card)
    })
    $("#editUserModal").modal("show")
}

function edit_remove_role(role) {
    const _user_roles = $("#user-roles")
    if (edit_add_roles.includes(role)) {
        _user_roles.html("")
        let values = []
        edit_add_roles.forEach(function (r) {
            if (role !== r) {
                values.push(r)
            }
        })
        edit_add_roles = values
        edit_add_roles.forEach(function (r) {
            const role_card = `<div class="alert alert-primary sq" role="alert" style="cursor: pointer;" onclick="edit_remove_role('` + r + `')">`
                + r + `</div>`
            _user_roles.append(role_card)
        })
    }
}

function reset_pw() {
    if (editing_user == null)
        return
    $.ajax({
        url: "/api/users/reset_pw/" + editing_user,
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data["success"]
            console.log(data)
            if (success) {
                const info = "New password: " + data.password
                $("#reset-dialogue").html(info)
            } else {
                $("#reset-dialogue").html("Failed to reset password: " + data.reason)
            }
        }
    })
}

function edit_add_role(role) {
    if (!edit_add_roles.includes(role)) {
        edit_add_roles.push(role)
        const role_card = `<div class="alert alert-primary sq" role="alert" style="cursor: pointer;" onclick="edit_remove_role('` + role + `')">`
            + role + `</div>`
        $("#user-roles").append(role_card)
    }
}