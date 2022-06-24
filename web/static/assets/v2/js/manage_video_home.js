let movies = []
let tv_shows = []
let editing_movie = null

function goto(loc) {
    window.location.href = loc;
}

function get_movie_object(uid) {
    for (let i = 0; i < movies.length; i++) {
        let movie = movies[i]
        if (movie["_id"] === uid)
            return movie
    }
    return null
}

function get_show_object(uid) {
    for (let i = 0; i < tv_shows.length; i++) {
        let show = tv_shows[i]
        if (show["_id"] === uid)
            return show
    }
    return null
}

function open_add_dialogue(tp) {
    const ids = ["add-tv-base-path", "add-tv-name", "add-tv-thumb", "add-name", "add-thumb", "add-file"]
    ids.forEach(function (id) {
        $("#" + id).val("")
    })
    if (tp === "movie") {
        $("#addMovieModal").modal("show")
    } else if (tp === "show") {
        $("#addShowModal").modal("show")
    }
}

function edit_show(uid) {
    goto("/manage/video/show/" + uid)
}

function load_movies() {
    $.ajax({
        url: "/api/movies?raw=true",
        method: 'GET',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            let success = data.success;
            if (success) {
                movies = data["movies"]
                list_movies(null)
            }
        }
    });
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

function search() {
    let search_value = $("#search").val()
    if (search_value.length < 1) {
        list_movies(null)
        list_shows(null)
    } else {
        list_movies(search_value)
        list_shows(search_value)
    }
}

function list_movies(search_value) {
    const _movie_list = $("#movie-list")
    const _movie_mobile_list = $("#mobile-movie-list")
    _movie_list.html("")
    if (search_value !== null) {
        search_value = search_value.toLowerCase().replace("-", " ")
    }
    movies = sort_movies(movies)
    let count = 0
    movies.forEach(function (movie) {
        if (search_value == null || movie.name.toLowerCase().includes(search_value)) {
            let year = null
            if (movie.hasOwnProperty("year")) {
                year = movie.year
            }
            _movie_list.append(get_movie_entry(movie.name, movie["_id"], year))
            _movie_mobile_list.append(get_movie_mobile_entry(movie.name, movie["_id"], year))
            count++;
        }
    })
    $("#movie-counts").html(count + " Movies")
}

function list_shows(search_value) {
    const _show_list = $("#show-list")
    const _show_mobile_list = $("#mobile-show-list")
    _show_list.html("")
    if (search_value !== null) {
        search_value = search_value.toLowerCase().replace("-", " ")
    }
    let shows = sort_shows(tv_shows)
    let count = 0
    shows.forEach(function (show) {
        if (search_value == null || show.name.toLowerCase().includes(search_value)) {
            let seasons = show.seasons
            let keys = Object.keys(seasons)
            let season_count = keys.length
            _show_list.append(get_show_entry(show.name, show["_id"], season_count))
            _show_mobile_list.append(get_show_mobile_entry(show.name, show["_id"], season_count))
            count++;
        }
    })
    $("#show-counts").html(count + " TV Shows")
}

function get_movie_mobile_entry(name, movie_id, year) {
    return `<div class="alert alert-primary" role="alert" onclick="edit_movie('` + movie_id +
        `')" style="cursor:pointer;">` + name + `</div>`
}

function get_movie_entry(name, movie_id, year) {
    if (year !== null && year.toString().length > 1) {
        return `<div class="row item">
                    <div class="col-7">` + name + `</div>
                    <div class="col-3">(` + year + `)</div>
                    <div class="col-2"><img src="/assets/img/edit-button.svg"
                onclick="edit_movie('` + movie_id + `')" style="cursor:pointer;"></div>
                </div>`
    }
    return `<div class="row item">
                    <div class="col-10">` + name + `</div>
                    <div class="col-2"><img src="/assets/img/edit-button.svg"
                onclick="edit_movie('` + movie_id + `')" style="cursor:pointer;"></div>
                </div>`
}

function get_show_mobile_entry(name, show_id, seasons) {
    return `<div class="alert alert-info" role="alert" onclick="edit_show('` + show_id +
        `')" style="cursor:pointer;">` + name + `</div>`
}

function get_show_entry(name, show_id, seasons) {
    let entry = `<div class="row item">
                    <div class="col-8">` + name + `</div>
                    <div class="col-2">` + seasons + `</div>
                    <div class="col-2"><img src="/assets/img/edit-button.svg"
                onclick="edit_show('` + show_id + `')" style="cursor:pointer;"></div>
                </div>`
    return entry
}

function add_movie() {
    let name = $("#add-name").val()
    let thumb = $("#add-thumb").val()
    let file = $("#add-file").val()
    let toSend = {
        "name": name,
        "thumb": thumb,
        "file": file
    }
    $.ajax({
        url: "/api/movies",
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
                $("#add-name").val("")
                $("#add-thumb").val("")
                $("#add-file").val("")
                $("#search").val("")
                load_movies()
                $("#addMovieModal").modal("hide")
            }
        }
    })
}

function add_show() {
    let name = null
    let thumb = "default.png"
    let base_path = null
    name = $("#add-tv-name").val()
    thumb = $("#add-tv-thumb").val()
    base_path = $("#add-tv-base-path").val()
    if (name == null || name.length < 0) {
        return
    }
    if (thumb == null || thumb.length < 0) {
        thumb = "default.png"
    }
    if (base_path == null || base_path.length < 0) {
        base_path = name.replace(/ /g, "_").toLowerCase()
    }
    let toSend = {
        "name": name,
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
                const ids = ["add-tv-name", "add-tv-thumb", "add-tv-base-path"]
                ids.forEach(function (id) {
                    $("#" + id).val("")
                })
                load_shows()
                $("#addShowModal").modal("hide")
            }
        }
    })
}

function delete_movie() {
    if (editing_movie === null)
        return
    $.ajax({
        url: "/api/movies/" + editing_movie,
        method: 'DELETE',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
        },
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (data) {
            const success = data["success"]
            if (success) {
                load_movies()
                $("#editMovieModal").modal("hide")
                editing_movie = null
            }
        }
    })
}

function save_movie() {
    if (editing_movie === null)
        return
    const name = $("#edit-name").val()
    const thumb = $("#edit-thumb").val()
    const file = $("#edit-file").val()
    const year = $("#edit-year").val()
    const desc = $("#edit-desc").val()
    let toSend = {}
    if (name != null && name !== "N/A" && name.length > 0) {
        toSend["name"] = name
    }
    if (desc != null && desc !== "N/A" && desc.length > 0) {
        toSend["description"] = desc
    }
    if (thumb != null && thumb !== "N/A" && thumb.length > 0) {
        toSend["thumb"] = thumb
    }
    if (file != null && file !== "N/A" && file.length > 0) {
        toSend["file"] = file
    }
    if (year != null) {
        toSend["year"] = year
    }
    $.ajax({
        url: "/api/movies/" + editing_movie,
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
                $("#edit-name").val("")
                $("#edit-description").val("")
                $("#edit-thumb").val("")
                $("#edit-file").val("")
                load_movies()
                $("#editMovieModal").modal("hide")
            }
        }
    })
}

function edit_movie(uid) {
    const movie = get_movie_object(uid)
    if (movie === null)
        return
    editing_movie = uid
    let year = ""
    if (movie.hasOwnProperty("year"))
        year = movie["year"]
    $("#edit-name").val(movie["name"])
    $("#edit-thumb").val(movie["thumb"])
    $("#edit-file").val(movie["file"])
    $("#edit-year").val(year)
    if (movie.hasOwnProperty("year"))
        $("#edit-year").val(movie["year"])
    if (movie.hasOwnProperty("description")) {
        $("#edit-desc").val(movie["description"])
    }
    $("#editMovieModal").modal("show")
}

$(document).ready(function () {
    load_shows()
    load_movies()
})