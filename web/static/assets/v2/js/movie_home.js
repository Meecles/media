let movie_data = {}
let previewing = null;

function get_card(movie_id, idv, name, description, thumbnail, meta) {
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
    let card = `<article class="style1" onclick="preview('` + movie_id + `')"><span class="image">
        <img class="thumb" src="/thumbs/default.png" data-src="/` + thumbnail + `" alt="" draggable="false" /></span>`;
    if (text_displayed) {
        card = card + `<div class="card-element"><h2 class="` + text_position_class + `">` + name + `</h2>`;
    }
    if (!(description == null || description === "N/A"))
        card = card + `<div class="content"><p>` + description + `</p></div>`;
    card = card + `</div></article>`;
    return card;
}

function preview(uid) {
    movie_data.forEach(function (movie) {
        if (movie["_id"] === uid) {
            let desc = movie["description"];
            if (desc == null || desc === "N/A") {
                desc = ""
            }
            const _thumb = $("#describeMovieThumb");
            $('#describeMovieName').html(movie["name"])
            $('#describeMovieDescription').html(desc)
            _thumb.html(`<img draggable="false" src="` + movie["thumb"] +
                `" style="cursor: pointer;max-width: 207px;max-height: 300px;"/>`)
            _thumb.attr("onclick", "goto('/watch/movie/" + movie["idv"] + "')");
            previewing = movie["idv"]
            $('#describeMovieModal').modal('show')
        }
    })
}

function play_movie() {
    if (previewing == null)
        return;

    goto("/watch/movie/" + previewing)
}

function search() {
    let srch = $("#movie-search")
    list_movies(srch.val())
}

function list_movies(value) {
    let _movies = $("#movie-list")
    _movies.html("")
    let movies = movie_data
    let map = {}
    let names = []
    for (let i = 0; i < movies.length; i++) {
        let movie = movies[i]
        let title = movie["name"]
        const hidden = movie["init_hide"]
        if (value == null || value.length < 1 || title.toLowerCase().includes(value.toLowerCase())) {
            let description = "N/A"
            let year = "N/A";
            if (movie.hasOwnProperty("year"))
                year = movie["year"]
            let meta = {
                "preview_position": movie["preview_position"],
                "year": year.toString()
            }
            const card = get_card(movie["_id"], movie["idv"], title, description, movie["thumb"], meta)
            map[title] = card
            if (!hidden || (value != null && value.length > 0)) {
                names.push(title)
            }
        }
    }
    names = sort_titles(names)

    for (let i = 0; i < names.length; i++) {
        const name = names[i]
        const card = map[name]
        _movies.append(card)
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
        url: "/api/movies",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                let movies = data["movies"]
                movie_data = movies
                list_movies(null)
            }
        }
    });
})
