let movies = []

function get_movie_entry(name, movie_id) {
    let entry = `<div class="alert alert-secondary" role="alert">
            <div class="row" style="margin-top: -5px; margin-bottom: -5px;">
                <div class="col-10" style="color: #24292e;">` + name + `</div>
                <div class="col-2"><img class="float-right" src="/assets/img/edit-button.svg" 
                onclick="edit_movie('` + movie_id + `')" style="cursor:pointer;"></div>
            </div>
        </div>`
    return entry
}

function edit_movie(movie_id) {
    let movie = null;
    for (let i = 0; i < movies.length; i++) {
        let m = movies[i]
        if (m["_id"] === movie_id) {
            movie = m
            break
        }
    }
    $("#edit-name").val(movie["name"])
    $("#movie-id").val(movie["_id"])
    $("#edit-description").val(movie["description"])
    $("#edit-thumb").val(movie["thumb"])
    $("#edit-file").val(movie["file"])
    $("#editMovieModal").modal("show")
}

function open_add_movie() {
    let name = $("#add-name").val("")
    let desc = $("#add-description").val("")
    let thumb = $("#add-thumb").val("")
    let file = $("#add-file").val("")
    $("#addMovieModal").modal("show")
}

function add_movie() {
    let name = $("#add-name").val()
    let desc = $("#add-description").val()
    let thumb = $("#add-thumb").val()
    let file = $("#add-file").val()
    let toSend = {
        "name": name,
        "description": desc,
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
                $("#add-description").val("")
                $("#add-thumb").val("")
                $("#add-file").val("")
                load_movies()
                $("#addMovieModal").modal("hide")
            }
        }
    })
}

function save_movie() {
    let movie_id = $("#movie-id").val()
    let name = $("#edit-name").val()
    let desc = $("#edit-description").val()
    let thumb = $("#edit-thumb").val()
    let file = $("#edit-file").val()
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
    $.ajax({
        url: "/api/movies/" + movie_id,
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

function list_movies(search) {
    let _list = $("#movie-list")
    let map = {}
    let titles = []
    movies.forEach(function (movie) {
        let title = movie["name"]
        if (search == null || title.toLowerCase().includes(search.toLowerCase())) {
            titles.push(title)
            map[title] = movie["_id"]
        }
    })
    if (titles.length === movies.length) {
        if (titles.length === 1) {
            $("#movie-count").html("(" + titles.length + " movie)")
        } else {
            $("#movie-count").html("(" + titles.length + " movies)")
        }
    } else {
        $("#movie-count").html("(Showing " + titles.length + " / " + movies.length + " movies)")
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
        _list.append(get_movie_entry(title, map[title]))
    })
}