let active_tab = "roles"
let group_edit = false
let group_editing = null
let group_movies = {}
let group_shows = {}
let video_groups = []
let all_movies = []
let all_shows = []
let movies_to_add = []
let shows_to_add = []

function get_video_group(uid) {
    for (let i = 0; i < video_groups.length; i++) {
        const group = video_groups[i]
        if (group["_id"] === uid) {
            return group
        }
    }
    return null
}

function set_tab_active(tab) {
    active_tab = tab
    const _rt = $("#tab-roles")
    const _vg = $("#tab-video-groups")
    const _mgn = $(".mgn")
    if (tab === "roles") {
        _mgn.removeClass("btn-info")
        _mgn.removeClass("btn-outline-info")
        $("#add-group-btn").hide()
        $("#add-role-btn").show()
        _rt.addClass("btn-info")
        _vg.addClass("btn-outline-info")
        cancel_group_edit()
    } else if (tab === "video_groups") {
        editing_role = null
        if (!group_edit) {
            load_video_groups()
            $("#generic-search").val("")
            _mgn.removeClass("btn-info")
            _mgn.removeClass("btn-outline-info")
            _vg.addClass("btn-info")
            _rt.addClass("btn-outline-info")
            $("#add-role-btn").hide()
            $("#add-group-btn").show()
        }
    }
}

function tab(tab) {
    set_tab_active(tab)
    if (tab === "roles") {
        $(".container-video-groups").hide()
        $(".container-roles").show()
    } else if (tab === "video_groups") {
        $(".container-video-groups").show()
        $(".container-roles").hide()
    }
}

function edit_remove_item(item) {
    const _item = $("#" + group_editing + "-" + item)
    if (!_item.hasClass("wiggle") || !group_edit)
        return
    const parts = item.split("-")
    const type = parts[0]
    const uid = parts[1] + "-" + parts[2] + "-" + parts[3] + "-" + parts[4] + "-" + parts[5]
    if (type === "movie") {
        delete group_movies[uid]
        _item.remove()
    } else if (type === "show") {
        delete group_shows[uid]
        _item.remove()
    }
}

function edit_group(uid) {
    const group = get_video_group(uid)
    if (group == null) {
        return
    }
    $("#generic-search").attr("disabled", "disabled")
    group_editing = uid
    $(".edit-start").hide()
    $(".edit-btns-" + uid).show()
    const _name = $("#group-name-" + uid)
    _name.html(`<input id="group-name-box" type="text" class="form-control">`)
    $("#group-name-box").val(group["name"])
    group_movies = group["movie_names"]
    group_shows = group["show_names"]
    Object.keys(group_movies).forEach(function (movie) {
        $("#" + uid + "-movie-" + movie).addClass("wiggle")
    })
    Object.keys(group_shows).forEach(function (show) {
        $("#" + uid + "-show-" + show).addClass("wiggle")
    })
    group_edit = true
}

function save_edit() {
    const uid = group_editing
    if (uid == null) {
        return
    }
    const group = get_video_group(uid)
    let name = group["name"]
    let val_name = $("#group-name-box").val()
    if (val_name.length > 0) {
        name = val_name
    }
    let toSend = {
        "name": name,
        "movies": group_movies,
        "shows": group_shows
    }
    $.ajax({
        url: "/api/video_groups/" + uid,
        method: 'PUT',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                $("#group-" + uid).remove()
                cancel_group_edit_run(true)
                load_video_groups()
            }
        }
    });
}

function cancel_group_edit() {
    cancel_group_edit_run(false)
}

function cancel_group_edit_run(bypass_reload) {
    $(".btn-sm").hide()
    $(".edit-start").show()
    const _search = $("#generic-search")
    if (group_editing != null) {
        const _name = $("#group-name-" + group_editing)
        const group = get_video_group(group_editing)
        _name.html(`<h5>` + group["name"] + `</h5>`)
        group_editing = null
    }
    $(".wiggle").removeClass("wiggle")
    if (!bypass_reload)
        load_video_groups()
    _search.removeAttr("disabled")
    _search.val("")
    group_movies = {}
    group_shows = {}
    group_edit = false
}

function get_group_card(group) {
    const name = group["name"]
    const uid = group["_id"]
    let movie_tags = ""
    let show_tags = ""
    const movies = group["movies"]
    const shows = group["shows"]
    movies.forEach(function (movie) {
        const movie_name = group["movie_names"][movie]
        movie_tags = movie_tags + `<h4 id="` + uid + `-movie-` + movie + `"><span class="badge badge-primary" onclick="edit_remove_item('movie-` + movie + `')">` +
            movie_name + `</span></h4>`
    })
    shows.forEach(function (show) {
        const show_name = group["show_names"][show]
        show_tags = show_tags + `<h4 id="` + uid + `-show-` + show + `"><span class="badge badge-info" onclick="edit_remove_item('show-` + show + `')">` +
            show_name + `</span></h4>`
    })
    let card = `<div class="col-lg-5 col-sm-12 col-md-10 col-xl-5" style="margin: 30px;">
<div id="group-` + uid + `" class="card" style="width: 100%">
                <div class="card-body">
                    <div class="card-title center-txt">
                        <div class="row">
                            <div class="col-6" id="group-name-` + uid + `">
                                <h5>` + name + `</h5>
                            </div>
                            <div class="col-6">
                                <button type="button" class="edit-init edit-start btn btn-sm btn-outline-light float-right"
                                    onclick="edit_group('` + uid + `')">Edit</button>
                                <button type="button" class="edit-delete edit-start btn btn-sm btn-outline-danger float-right"
                                style="margin-right: 5px;" onclick="delete_group('` + uid + `')">Delete</button>
                                <button type="button" class="edit-btns-` + uid + ` btn btn-sm btn-outline-success float-right" style="display: none; margin-left: 5px;"
                                    onclick="save_edit()">Save</button>
                                <button type="button" class="edit-btns-` + uid + ` btn btn-sm btn-outline-secondary float-right" style="display: none; margin-left: 5px;"
                                    onclick="cancel_group_edit()">Cancel</button>
                                <button type="button" class="edit-btns-` + uid + ` btn btn-sm btn-outline-light float-right" style="display: none;"
                                    onclick="add_content_modal()">Add</button>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-6">` + movie_tags + `</div>
                        <div class="col-6">` + show_tags + `</div>
                    </div>
                </div>
            </div></div>`
    return card
}

function add_search() {
    search_modal_content()
}

function add_content_modal() {
    $("#add-search").val("")
    $("#add-list").html(`<span class="badge badge-danger">None</span>`)
    movies_to_add = []
    shows_to_add = []
    search_modal_content()
    $("#addGroupContentModal").modal("show")
}

function search() {
    if (active_tab === "video_groups") {
        list_groups($("#generic-search").val())
    }
    else if (active_tab === "roles"){
        list_roles()
    }
}

function group_filter_show(group, search) {
    const name = group["name"]
    return search == null || name.toLowerCase().includes(search.toLowerCase());
}

function list_groups(search) {
    const _groups = $("#group-list")
    _groups.html("")
    video_groups.forEach(function (group) {
        if (group_filter_show(group, search)) {
            _groups.append(get_group_card(group))
        }
    })
}

function delete_group(uid) {
    $.ajax({
        url: "/api/video_groups/" + uid,
        method: 'DELETE',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                $("#group-" + uid).remove()
                load_video_groups_with_search(true)
            }
            else {
                const reason = data["reason"]
                alert(reason)
            }
        }
    });
}

function get_item_name(type, uid) {
    if (type === "movie") {
        for (let i = 0; i < all_movies.length; i++) {
            const movie = all_movies[i]
            if (movie["_id"] === uid) {
                return movie["name"]
            }
        }
    }
    if (type === "show") {
        for (let i = 0; i < all_shows.length; i++) {
            const show = all_shows[i]
            if (show["_id"] === uid) {
                return show["name"]
            }
        }
    }
    return ""
}

function add_queue() {
    const uid = group_editing
    let toSend = {
        "add_movies": movies_to_add,
        "add_shows": shows_to_add
    }
    $.ajax({
        url: "/api/video_groups/" + uid,
        method: 'PUT',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                $("#group-" + uid).remove()
                cancel_group_edit_run(true)
                load_video_groups()
                $("#addGroupContentModal").modal("hide")
            }
        }
    });
}

function queue_item(type, uid) {
    $("#add-" + type + "-" + uid).remove()
    const _list = $("#add-list")
    if (type === "movie") {
        if (!movies_to_add.includes(uid)) {
            movies_to_add.push(uid)
        }
    } else if (type === "show") {
        if (!shows_to_add.includes(uid)) {
            shows_to_add.push(uid)
        }
    }
    if (shows_to_add.length < 1 && movies_to_add.length < 1) {
        _list.html(`<span class="badge badge-danger">None</span>`)
    } else {
        _list.html("")
        movies_to_add.forEach(function (uid) {
            const name = get_item_name("movie", uid)
            _list.append(`<span class="badge badge-primary" style="margin: 3px; border-radius: 0;">` + name + `</span>`)
        })
        shows_to_add.forEach(function (uid) {
            const name = get_item_name("show", uid)
            _list.append(`<span class="badge badge-info" style="margin: 3px; border-radius: 0;">` + name + `</span>`)
        })
    }
}

function search_modal_content() {
    let search = $("#add-search").val()
    const _movies = $("#modal-movies")
    const _shows = $("#modal-shows")
    _movies.html("")
    _shows.html("")
    all_movies.forEach(function (movie) {
        const name = movie["name"]
        const uid = movie["_id"]
        if (search.toLowerCase().length < 1 || name.toLowerCase().includes(search.toLowerCase())) {
            _movies.append(`<div id="add-movie-` + uid + `" class="alert alert-primary" role="alert" style="cursor: pointer;"
                    onclick="queue_item('movie', '` + uid + `')">` + name + `</div>`)
        }
    })
    all_shows.forEach(function (show) {
        const name = show["name"]
        const uid = show["_id"]
        if (search.toLowerCase().length < 1 || name.toLowerCase().includes(search.toLowerCase())) {
            _shows.append(`<div id="add-show-` + uid + `" class="alert alert-info" role="alert" style="cursor: pointer;"
                    onclick="queue_item('show', '` + uid + `')">` + name + `</div>`)
        }
    })
}

function modal_content() {
    $.ajax({
        url: "/api/videos",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                all_movies = data["movies"]
                all_shows = data["shows"]
                $("#add-search").val("")
                search_modal_content()
            }
        }
    });
}

function add_group() {
    $.ajax({
        url: "/api/video_groups",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                $("#generic-search").val("")
                load_video_groups()
            }
        }
    });
}

function load_video_groups() {
    load_video_groups_with_search(false)
}

function load_video_groups_with_search(srh) {
    $.ajax({
        url: "/api/video_groups?translate=both",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                video_groups = data["groups"]
                if (srh) {
                    search()
                } else {
                    list_groups(null)
                }
            }
        }
    });
}