let tv_shows = null

function load_shows() {
    $.ajax({
        url: "/api/shows",
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

function get_card(show_id, show_name, thumb) {
    if (thumb === "N/A") {
        thumb = "/thumbs/default.png"
    }
    let card = `<div class="col-sm-8 col-md-4 col-lg-3 col-xl-2" style="margin: 30px;cursor: pointer;" onclick="goto('/shows/` + show_id + `')">
        <div class="card" style="width: 16rem;height: 280px;">
            <div class="card-body">
                <h5 class="card-title center-txt">` + show_name + `</h5>
                <img src="/thumbs/default.png" data-src="` + thumb + `" class="center-img" draggable="false" style="max-height: 220px;">
            </div>
        </div>
    </div>`
    return card
}

function goto(loc) {
    window.location.href = loc;
}

function get_show(name) {
    for (let i = 0; i < tv_shows.length; i++) {
        let show = tv_shows[i]
        let title = show["name"]
        if (title === name) {
            return show
        }
    }
    return null
}

function search() {
    let srch = $("#show-search")
    const value = srch.val()
    list_shows(value)
}

function list_shows(search) {
    const _show_list = $("#show-list")
    _show_list.html("")
    let names = []
    tv_shows.forEach(function (show) {
        names.push(show["name"])
    })
    names = names.sort(
        function (a, b) {
            if (a.toLowerCase() < b.toLowerCase()) return -1;
            if (a.toLowerCase() > b.toLowerCase()) return 1;
            return 0;
        }
    )
    let shows = []
    names.forEach(function (name) {
        if (search == null || name.toLowerCase().includes(search.toLowerCase())) {
            let show = get_show(name)
            if (show != null) {
                shows.push(show)
            }
        }
    })
    for (let i = 0; i < shows.length; i++) {
        let show = shows[i]
        const sid = show["_id"]
        const name = show["name"]
        const thumb = show["thumb"]
        let card = get_card(sid, name, thumb)
        _show_list.append(card)
        if (i % 10 === 0 && i < 30) {
            $("img").unveil();
        }
    }
    $("img").unveil();
}

$(document).ready(function () {
    load_shows()
})