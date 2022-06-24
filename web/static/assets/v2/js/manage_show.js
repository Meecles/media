const generic_fields = ["edit-name", "edit-description", "edit-thumb", "edit-base-path"]
let hold_edit_name = ""
let hold_edit_desc = ""
let hold_edit_thumb = ""
let hold_edit_base_path = ""
let all_seasons = {}

function goto(loc) {
    window.location.href = loc;
}

function add_season() {
    let num = $("#add-season-number").val().toString()
    let name = $("#add-season-name").val()
    const toSend = {
        "num": num,
        "name": name
    }
    $.ajax({
        url: "/api/shows/" + _show_id + "/add_season",
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data["success"]
            if (success) {

                populate()
                $("#addSeasonModal").modal("hide")
            }
        }
    })
}

function open_add_season() {
    let keys = Object.keys(all_seasons)
    let season_nums = []
    keys.forEach(function (key) {
        let season = all_seasons[key]
        season_nums.push(season["season"])
    })
    let num = 1
    while (season_nums.includes(num)) {
        num++
    }
    $("#add-season-name").val("Season " + num)
    $("#add-season-number").val(num)
    $("#addSeasonModal").modal("show")
}

function get_mobile_season_entry(name, season_id, episodes) {
    let entry = `<div class="alert alert-secondary" role="alert">
            <div class="row" style="margin-top: -5px; margin-bottom: -5px;">
                <div class="col-8" style="color: #24292e;">` + name + `</div>
                <div class="col-2" style="text-align: right; color: #24292e;">` + episodes + `</div>
                <div class="col-2">
                <a href="/manage/video/show/` + _show_id + `/` + season_id + `">
                    <img class="float-right" src="/assets/img/edit-button.svg" style="cursor:pointer;">
                </a></div>
            </div>
        </div>`
    return entry
}

function get_season_entry(name, season_id, episodes) {
    let entry = `<div class="row">
            <div class="col-7">` + name + `</div>
            <div class="col-2">` + episodes + `</div>
            <div class="col-3">
            <button class="btn btn-outline-dark btn-sm float-right txt-white" onclick="goto('/manage/video/show/` +
        _show_id + `/` + season_id + `')">Edit</button>
            </div>
            </div><p style="margin-top: -30px;"></p>`
    return entry
}

function cancel_edit() {
    generic_fields.forEach(function (item) {
        $("#" + item).attr('disabled', 'disabled');
    })
    $("#edit-name").val(hold_edit_name)
    $("#edit-description").val(hold_edit_desc)
    $("#edit-thumb").val(hold_edit_thumb)
    $("#edit-base-path").val(hold_edit_base_path)
    hold_edit_name = ""
    hold_edit_desc = ""
    hold_edit_thumb = ""
    hold_edit_base_path = ""
    $("#edit-generic-btn").show()
    $("#save-generic-btn").hide()
    $("#cancel-generic-btn").hide()
}

function save_editing() {
    generic_fields.forEach(function (item) {
        $("#" + item).attr('disabled', 'disabled');
    })
    hold_edit_name = ""
    hold_edit_desc = ""
    hold_edit_thumb = ""
    hold_edit_base_path = ""
    $("#edit-generic-btn").show()
    $("#save-generic-btn").hide()
    $("#cancel-generic-btn").hide()
    let toSend = {
        "name": $("#edit-name").val(),
        "description": $("#edit-description").val(),
        "thumb": $("#edit-thumb").val(),
        "base_path": $("#edit-base-path").val()
    }
    $.ajax({
        url: "/api/shows/" + _show_id,
        method: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data["success"]
            if (success) {
                const show = data["show"]
                $("#edit-name").val(show["name"])
                $("#show-name-title").html("Edit - " + show["name"])
                $("#edit-description").val(show["description"])
                $("#edit-thumb").val(show["thumb"])
                $("#edit-base-path").val(show["base_path"])
            }
        }
    })
}

function enable_editing() {
    hold_edit_name = $("#edit-name").val()
    hold_edit_desc = $("#edit-description").val()
    hold_edit_thumb = $("#edit-thumb").val()
    hold_edit_base_path = $("#edit-base-path").val()
    generic_fields.forEach(function (item) {
        $("#" + item).removeAttr("disabled")
    })
    $("#edit-generic-btn").hide()
    $("#save-generic-btn").show()
    $("#cancel-generic-btn").show()
}

function season_info(seasons) {
    let list = []
    const keys = Object.keys(seasons)
    all_seasons = seasons
    keys.forEach(function (key) {
        let season = seasons[key]
        season["key"] = key
        list.push(season)
    })
    list = list.sort(
        function (a, b) {
            if (a["season"] < b["season"]) return -1;
            if (a["season"] > b["season"]) return 1;
            return 0;
        }
    )
    const _season_list = $("#season-list")
    _season_list.html("")
    list.forEach(function (item) {
        let episodes = 0
        if (item.hasOwnProperty("episodes")) {
            episodes = item["episodes"]
        }
        _season_list.append(get_season_entry(item["name"], item["key"], episodes))
    })
}

function populate() {
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
                let tv_show = data["shows"][0]
                $("#edit-name").val(tv_show["name"])
                $("#show-name-title").val("Edit - " + tv_show["name"])
                if (tv_show.hasOwnProperty("description")) {
                    $("#edit-description").val(tv_show["description"])
                } else {
                    $("#edit-description").val("N/A")
                }
                if (tv_show.hasOwnProperty("thumb")) {
                    $("#edit-thumb").val(tv_show["thumb"])
                } else {
                    $("#edit-thumb").val("default.png")
                }
                $("#edit-base-path").val(tv_show["base_path"])
                season_info(tv_show["seasons"])
            }
        }
    });
}

$(document).ready(function () {
    $("#save-generic-btn").hide()
    $("#cancel-generic-btn").hide()
    generic_fields.forEach(function (item) {
        $("#" + item).attr('disabled', 'disabled');
    })
    populate()
})