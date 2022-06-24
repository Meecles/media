let show_data = {}


function get_card(show_id, name, description, thumbnail, meta) {
    let text_position_class = "movie-card-text-above";
    let text_displayed = true;
    if (meta != null) {
        if (meta.hasOwnProperty("preview_position")) {
            const pos = meta["preview_position"]
            if (pos === "none") {
                text_displayed = false;
            } else {
                if (pos === "above"){
                    text_position_class = "movie-card-text-above"
                }
                else if (pos === "top") {
                    text_position_class = "movie-card-text-top"
                } else if (pos === "bottom") {
                    text_position_class = "movie-card-text-bottom"
                } else if (pos === "center") {
                    text_position_class = "movie-card-text-center"
                }
            }
        }
        if (meta.hasOwnProperty("year")){
            const year = meta.year.toString()
            if (year !== "N/A"){
                const year_str = "(" + year + ")"
                if (name.endsWith(year_str)){
                    name = name.replace(year_str, "")
                }
                name = name + " <small style='font-size: 12px;color: gray; margin-bottom: 20%;'>" + year_str + "</small>"
            }
        }
    }
    let card = `<article class="style1" onclick="show_click('` + show_id + `')"><span class="image">
        <img class="thumb" src="/thumbs/default.png" data-src="/` + thumbnail + `" alt="" draggable="false" /></span>`;
    if (text_displayed) {
        card = card + `<div class="card-element"><h2 class="` + text_position_class + `">` + name + `</h2>`;
    }
    if (!(description == null || description === "N/A"))
        card = card + `<div class="content"><p>` + description + `</p></div>`;
    card = card + `</div></article>`;
    return card;
}

function show_click(uid) {
    show_data.forEach(function (show) {
        if (show["_id"] === uid) {
            goto("/shows/" + uid)
        }
    })
}

function search() {
    let srch = $("#show-search")
    list_shows(srch.val())
}

function list_shows(value) {
    let _shows = $("#show-list")
    _shows.html("")
    let shows = show_data
    let map = {}
    let names = []
    for (let i = 0; i < shows.length; i++) {
        let show = shows[i]
        let title = show["name"]
        const hidden = false
        if (value == null || value.length < 1 || title.toLowerCase().includes(value.toLowerCase())) {
            let description = "N/A"
            if (show.hasOwnProperty("description"))
                description = show["description"]
            const meta = {}
            const card = get_card(show["_id"], title, description, show["thumb"], meta)
            map[title] = card
            if (!hidden || (value != null && value.length > 0)) {
                names.push(title)
            }
        }
    }
    names = names.sort(
        function (a, b) {
            if (a.toLowerCase() < b.toLowerCase()) return -1;
            if (a.toLowerCase() > b.toLowerCase()) return 1;
            return 0;
        }
    )
    for (let i = 0; i < names.length; i++) {
        const name = names[i]
        const card = map[name]
        _shows.append(card)
        if (i % 10 === 0 && i < 30) {
            $("img").unveil(400);
        }
    }
    $("img").unveil(400);
}

function goto(loc) {
    window.location.href = loc;
}

$(document).ready(function () {
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
                show_data = data["shows"]
                list_shows(null)
            }
        }
    });
})
