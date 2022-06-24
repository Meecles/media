function open_add_user() {
    let btn_cancel = `<button class="btn btn-secondary" type="button" data-dismiss="modal">Cancel</button>`
    let btn_add = `<button type="button" class="btn btn-primary" onclick="add_user()">Add</button>`
    let footer = $("#add-user-footer")
    footer.html(btn_cancel)
    footer.append(btn_add)
    $("#addUserModal").modal("show")
}

let add_roles = []
let edit_add_roles = []
let users_table = null
let users_data = {}
let editing_user = null;

function get_badge(role) {
    let input = role
    input = input.charAt(0).toUpperCase() + input.slice(1);
    return `<span class="badge badge-pill badge-info role-pill" onclick="remove_role('` +
        role + `')">` + input + `</span>&nbsp;`
}

function add_role(role) {
    if (!add_roles.includes(role)) {
        $("#role-badges").append(get_badge(role))
        add_roles.push(role)
    }
}

function remove_role(role) {
    if (add_roles.includes(role)) {
        let new_roles = []
        for (let i = 0; i < add_roles.length; i++) {
            const n_role = add_roles[i]
            if (!new_roles.includes(n_role) && n_role !== role) {
                new_roles.push(n_role)
            }
        }
        add_roles = new_roles
        $("#role-badges").html("")
        for (let i = 0; i < add_roles.length; i++) {
            let r = add_roles[i]
            $("#role-badges").append(get_badge(r))
        }
    }
}

function add_user() {
    const roles = add_roles
    const username = $("#new_username").val()
    if (roles.length < 1) {
        $("#response-message").html("Error: You must select at least one role")
        $("#response-message").addClass("text-danger")
        return;
    }
    if (username.length < 3) {
        $("#response-message").html("Error: Username must be at least 3 characters")
        $("#response-message").addClass("text-danger")
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
            $("#response-message").html("")
            $("#response-message").removeClass("text-danger")
            $("#response-message").removeClass("text-success")
            const success = data.success;
            if (success) {
                const pass = data["password"]
                $("#response-message").html("Success! Password: " + pass)
                $("#response-message").addClass("text-success")
                let btn_close = `<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>`
                $("#add-user-footer").html(btn_close)
            } else {
                $("#response-message").html(data["reason"])
                $("#response-message").addClass("text-danger")
            }
        }
    })
}


function get_edit_role_badge(name, color) {
    return `<span class="badge badge-pill badge-` + color + ` role-pill" onclick="edit_remove_role('` + name + `')">` + name + `</span>`
}

function edit_remove_role(role) {
    let roles = []
    for (let i = 0; i < edit_add_roles.length; i++) {
        if (edit_add_roles[i] !== role) {
            roles.push(edit_add_roles[i])
        }
    }
    edit_add_roles = roles;
    let _user_roles = $("#user-roles")
    _user_roles.html("")
    for (let i = 0; i < edit_add_roles.length; i++) {
        const role = edit_add_roles[i]
        const badge = get_edit_role_badge(role, "primary") + "&nbsp;"
        _user_roles.append(badge)
    }
}

function edit_add_role(role) {
    if (edit_add_roles.includes(role)) {
        return
    }
    let _user_roles = $("#user-roles")
    edit_add_roles.push(role)
    const badge = get_edit_role_badge(role, "primary") + "&nbsp;"
    _user_roles.append(badge)
}

function open_edit_user(uid) {
    edit_add_roles = []
    editing_user = uid
    let _mfa_enabled = $("#mfa_enabled")
    let _mfa_required = $("#mfa_required")
    let _user_roles = $("#user-roles")
    console.log("UID: " + uid)
    let user = users_data[uid]
    console.log(user)
    let username = user["username"]
    $("#edit-username").val(username)
    if (user["mfa_enabled"]) {
        _mfa_enabled.prop("checked", true);
        _mfa_enabled.removeAttr("disabled")
    } else {
        _mfa_enabled.prop("checked", false);
        _mfa_enabled.attr("disabled", true)
    }
    if (user["mfa_required"]) {
        _mfa_required.prop("checked", true);
    } else {
        _mfa_required.prop("checked", false);
    }
    _user_roles.html("")
    for (let i = 0; i < user["roles"].length; i++) {
        let role = user["roles"][i]
        edit_add_roles.push(role)
        const badge = get_edit_role_badge(role, "primary") + "&nbsp;"
        _user_roles.append(badge)
    }
    $("#editUserModal").modal("show")
}


function get_btns(uid) {
    let btn1 = `<i class="fas fa-edit" style="cursor:pointer;text-align: left;"` +
        ` onclick="open_edit_user('` + uid + `')"></i>`
    let btn2 = `<i class="fas fa-trash" style="cursor:pointer; text-align: right;" ` +
        `onclick="delete_user('` + uid + `')"></i>`
    return `<table style="opacity: 1; border: none;"><tbody><tr><td>` + btn1 + `</td><td>` + btn2 + `</td></tr></tbody></table>`
}

function get_role_badge(role, color) {
    return `<span class="badge badge-` + color + `">` + role + `</span>`
}

function populate() {
    if (users_table == null) {
        users_table = $('#users').DataTable({
            columns: [
                {
                    "width": "30%",
                    "data": "username",
                    "title": "Username"
                },
                {
                    "width": "30%",
                    "data": "roles",
                    "title": "Roles"
                },
                {
                    "width": "15%",
                    "data": "mfa_enabled",
                    "title": "MFA Enabled"
                },
                {
                    "width": "15%",
                    "data": "mfa_required",
                    "title": "MFA Required"
                },
                {
                    "width": "10%",
                    "data": "btns",
                    "title": ""
                }
            ]
        });
    }
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
                users_table.clear()
                let users = data.users;
                for (let i = 0; i < users.length; i++) {
                    const user = users[i]
                    let role_str = "";
                    let roles = user["roles"];
                    let valid_roles = user["valid_roles"]
                    for (let i = 0; i < roles.length; i++) {
                        let role = roles[i]
                        let color = "primary"
                        if (!valid_roles.includes(role)) {
                            color = "warning"
                        }
                        role_str = role_str + " " + get_role_badge(role, color)
                    }

                    let enabled = `<span class="badge badge-danger">Disabled</span>`
                    let required = `<span class="badge badge-danger">False</span>`
                    if (user["mfa_enabled"]) {
                        enabled = `<span class="badge badge-success">Enabled</span>`
                    }
                    if (user["mfa_required"]) {
                        required = `<span class="badge badge-success">True</span>`
                    }
                    let uid = user["_id"]
                    if (uid === undefined) {
                        uid = user["id"]
                    }
                    let btns = get_btns(uid)
                    let formatted_user_data = {
                        "username": user["username"],
                        "roles": role_str,
                        "mfa_enabled": enabled,
                        "mfa_required": required,
                        "btns": btns
                    }
                    users_data[uid] = user
                    users_table.row.add(formatted_user_data)
                }
                users_table.draw()

            } else {
                $("#table-wrapper").html("Failed to load table, are you logged in?")
            }
        }
    });
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
                populate()
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
            populate()
            $("#deleteUserModal").modal("hide")
        }
    })
}

function delete_user(uid) {
    const btn_no = `<button class="btn btn-secondary" type="button" data-dismiss="modal">No</button>`
    let btn_yes = `<button type="button" class="btn btn-danger" onClick="confirm_delete_user('` + uid + `')">Yes</button>`
    let del = $("#delete_user_footer")
    del.html("")
    del.append(btn_no)
    del.append(btn_yes)
    $("#deleteUserModal").modal("show")
}

$(document).ready(function () {

    $("#addUserModal").on('hidden.bs.modal', function () {
        $("#new_username").val("")
        add_roles = []
        $("#role-badges").html("")
        $("#response-message").html("")
        $("#response-message").removeClass("text-danger")
        $("#response-message").removeClass("text-success")
        populate()
    });

    populate()
});