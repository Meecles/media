let tv_shows = null

function get_show_entry(name, show_id, seasons) {
    let entry = `<div class="alert alert-secondary" role="alert">
            <div class="row" style="margin-top: -5px; margin-bottom: -5px;">
                <div class="col-8" style="color: #24292e;">` + name + `</div>
                <div class="col-2" style="color: #24292e;">` + seasons + `</div>
                <div class="col-2">
                <a href="/settings/videos/show/` + show_id + `">
                    <img class="float-right" src="/assets/img/edit-button.svg" style="cursor:pointer;">
                </a></div>
            </div>
        </div>`
    return entry
}

function open_add_show() {
    const ids = ["add-tv-name", "add-tv-description", "add-tv-thumb", "add-tv-base-path"]
    ids.forEach(function (id) {
        $("#" + id).val("")
    })
    $("#addShowModal").modal("show")
}

function add_show() {
    let name = null
    let desc = null
    let thumb = "default.png"
    let base_path = null
    name = $("#add-tv-name").val()
    desc = $("#add-tv-description").val()
    thumb = $("#add-tv-thumb").val()
    base_path = $("#add-tv-base-path").val()
    if (name == null || name.length < 0) {
        return
    }
    if (desc == null || desc.length < 0) {
        desc = "N/A"
    }
    if (thumb == null || thumb.length < 0) {
        thumb = "default.png"
    }
    if (base_path == null || base_path.length < 0) {
        base_path = name.replace(/ /g, "_").toLowerCase()
    }
    let toSend = {
        "name": name,
        "description": desc,
        "thumb": thumb,
        "base_path": base_path
    }
    $.ajax({
        url: "/api/shows",
        method: 'PUT',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        data: JSON.stringify(toSend),
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data["success"]
            if (success) {
                const ids = ["add-tv-name", "add-tv-description", "add-tv-thumb", "add-tv-base-path"]
                ids.forEach(function (id) {
                    $("#" + id).val("")
                })
                load_shows()
                $("#addShowModal").modal("hide")
            }
        }
    })
}

function load_shows() {
    $.ajax({
        url: "/api/shows?raw=true",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                tv_shows = data["shows"]
                list_shows(null)
            }
        }
    });
}

function list_shows(search) {
    let _list = $("#show-list")
    let map = {}
    let s_map = {}
    let titles = []
    tv_shows.forEach(function (show) {
        let title = show["name"]
        if (search == null || title.toLowerCase().includes(search.toLowerCase())) {
            titles.push(title)
            map[title] = show["_id"]
            s_map[title] = show["season_count"]
        }
    })
    if (titles.length === tv_shows.length) {
        if (titles.length === 1) {
            $("#show-count").html("(" + titles.length + " show)")
        } else {
            $("#show-count").html("(" + titles.length + " shows)")
        }
    } else {
        $("#show-count").html("(Showing " + titles.length + " / " + tv_shows.length + " shows)")
    }
    titles = titles.sort(
        function (a, b) {
            if (a.toLowerCase() < b.toLowerCase()) return -1;
            if (a.toLowerCase() > b.toLowerCase()) return 1;
            return 0;
        }
    )
    _list.html("")
    titles.forEach(function (title) {
        _list.append(get_show_entry(title, map[title], s_map[title]))
    })
}