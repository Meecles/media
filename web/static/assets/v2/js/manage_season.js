function goto(loc) {
    window.location.href = loc;
}

function go_back() {
    goto("/manage/video/show/" + _show_id)
}

let episodes = []
let b_name = null
let b_thumb = null
let b_base_path = null

function get_entry(name, episode, episode_id) {
    let entry = `<div class="row">
            <div class="col-1">` + episode + `</div>
            <div class="col-9">` + name + `</div>
            <div class="col-2">
            <button class="btn btn-outline-dark btn-sm float-right txt-white" onclick="edit_episode('` + episode_id + `')">Edit</button>
            </div>
            </div><p style="margin-top: -30px;"></p>`
    return entry
}

function edit_episode(episode_id) {
    let episode = null
    episodes.forEach(function (ep) {
        if (ep["_id"] === episode_id) {
            episode = ep
        }
    })
    if (episode == null) {
        return
    }
    $("#ep-edit-name").val(episode["name"])
    $("#ep-edit-thumb").val(episode["thumb"])
    $("#ep-edit-file").val(episode["file"])
    $("#ep-edit-id").val(episode["_id"])
    $("#editEpisodeModal").modal("show")
}

function save_episode() {
    let toSend = {
        "name": $("#ep-edit-name").val(),
        "thumb": $("#ep-edit-thumb").val(),
        "file": $("#ep-edit-file").val(),
    }
    const episode_id = $("#ep-edit-id").val()
    $.ajax({
        url: "/api/shows/" + _show_id + "/" + _season_id + "/" + episode_id,
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                load_data(false, true)
                $("#editEpisodeModal").modal("hide")
            }
        }
    });
}

function open_add_episode() {
    let nums = []
    episodes.forEach(function (episode) {
        let num = episode["episode"]
        nums.push(num)
    })
    let num = 1;
    while (nums.includes(num)) {
        num++
    }
    let auto_fill = "s" + _season_num + "e" + num + ".mp4"
    $("#add-file").val(auto_fill)
    $("#add-episode").val(num)
    $("#add-name").val("")
    $("#add-thumb").val("")
    $("#addEpisodeModal").modal("show")
}

function add_episode() {
    let toSend = {
        "name": $("#add-name").val(),
        "thumb": $("#add-thumb").val(),
        "file": $("#add-file").val(),
        "episode": $("#add-episode").val()
    }
    $.ajax({
        url: "/api/shows/" + _show_id + "/" + _season_id + "/add_episode",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                load_data(false, true)
                $("#addEpisodeModal").modal("hide")
            }
        }
    });
}

function enable_editing() {
    const boxes = ["edit-name", "edit-thumb", "edit-base-path"]
    $("#cancel-generic-btn").show()
    $("#save-generic-btn").show()
    $("#edit-generic-btn").hide()
    boxes.forEach(function (item) {
        $("#" + item).removeAttr("disabled")
    })
}

function save_editing() {
    const disable = ["edit-name", "edit-thumb", "edit-base-path"]
    disable.forEach(function (item) {
        $("#" + item).attr("disabled", "disabled")
    })
    const toSend = {
        "name": $("#edit-name").val(),
        "alt_thumb": $("#edit-thumb").val(),
        "base_path": $("#edit-base-path").val()
    }
    $.ajax({
        url: "/api/shows/" + _show_id + "/" + _season_id + "/edit_season",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                const season_data = data["season_data"]
                $("#edit-name").val(season_data["name"])
                $("#edit-base-path").val(season_data["base_path"])
                $("#edit-thumb").val(season_data["alt_thumb"])
                b_name = season_data["name"]
                b_thumb = season_data["alt_thumb"]
                b_base_path = season_data["base_path"]
            } else {
                $("#edit-name").val(b_name)
                $("#edit-thumb").val(b_thumb)
                $("#edit-base-path").val(b_base_path)
            }
        }
    });
    $("#cancel-generic-btn").hide()
    $("#save-generic-btn").hide()
    $("#edit-generic-btn").show()
}

function cancel_edit() {
    const disable = ["edit-name", "edit-thumb", "edit-base-path"]
    disable.forEach(function (item) {
        $("#" + item).attr("disabled", "disabled")
    })
    $("#cancel-generic-btn").hide()
    $("#save-generic-btn").hide()
    $("#edit-generic-btn").show()
    $("#edit-name").val(b_name)
    $("#edit-thumb").val(b_thumb)
    $("#edit-base-path").val(b_base_path)
}

function search() {
    const val = $("#search-episodes").val()
    if (val.length < 1) {
        list_episodes(null)
    } else {
        list_episodes(val)
    }
}

function list_episodes(search) {
    let _episode_list = $("#episode-list")
    _episode_list.html("")
    episodes.forEach(function (episode) {
        let name = episode["name"]
        let ep = episode["episode"]
        if (search == null || name.toLowerCase().includes(search.toLowerCase())) {
            let episode_id = episode["_id"]
            _episode_list.append(get_entry(name, ep, episode_id))
        }
    })
}

function load_data(load_generic, load_episodes) {
    if (load_generic) {
        $.ajax({
            url: "/api/shows?raw=true&filter=" + _show_id,
            method: 'GET',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
            },
            dataType: "json",
            contentType: "application/json;charset=utf-8",
            success: function (data) {
                let success = data.success;
                if (success) {
                    const show = data["shows"][0]
                    const season_data = show["seasons"][_season_id]
                    b_name = season_data["name"]
                    b_thumb = season_data["alt_thumb"]
                    b_base_path = season_data["base_path"]
                    $("#edit-name").val(b_name)
                    $("#edit-thumb").val(b_thumb)
                    $("#edit-base-path").val(b_base_path)
                }
            }
        });
    }
    if (load_episodes) {
        $.ajax({
            url: "/api/shows/" + _show_id + "/episodes/" + _season_id,
            method: 'GET',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
            },
            dataType: "json",
            contentType: "application/json;charset=utf-8",
            success: function (data) {
                let success = data.success;
                if (success) {
                    episodes = data["episodes"]
                    list_episodes(null)
                }
            }
        });
    }
}

$(document).ready(function () {
    $("#cancel-generic-btn").hide()
    $("#save-generic-btn").hide()
    const disable = ["edit-name", "edit-thumb", "edit-base-path"]
    disable.forEach(function (item) {
        $("#" + item).attr("disabled", "disabled")
    })
    load_data(true, true)
})
