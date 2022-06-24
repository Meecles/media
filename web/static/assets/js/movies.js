let movie_data = null;


function search() {
    let srch = $("#movie-search")
    list_movies(srch.val())
}


function list_movies(value) {
    let movie_list = $("#movie-list")
    movie_list.html("")
    let movies = movie_data
    let map = {}
    let names = []
    for (let i = 0; i < movies.length; i++) {
        let movie = movies[i]
        let title = movie["name"]
        const hidden = movie["init_hide"]
        if (value == null || value.length < 1 || title.toLowerCase().includes(value.toLowerCase())) {
            const card = get_card(movie["_id"], movie["idv"], title, movie["thumb"])
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
        $("#movie-list").append(card)
        if (i % 10 === 0 && i < 30) {
            $("img").unveil(400);
        }
    }
    $("img").unveil(400);
}

function get_card(uid, idv, movie_name, thumb) {
    if (thumb === "N/A") {
        thumb = "/thumbs/default.png"
    }
    let card = `<div class="col-sm-8 col-md-4 col-lg-3 col-xl-2" style="margin: 30px;cursor: pointer;" onclick="preview('` + uid + `')">
        <div class="card" style="width: 16rem;height: 320px;">
            <div class="card-body">
                <h5 class="card-title center-txt">` + movie_name + `</h5>
                <img src="/thumbs/default.png" data-src="` + thumb + `" class="center-img" draggable="false">
            </div>
        </div>
    </div>`
    return card
}

function preview(uid) {
    movie_data.forEach(function (movie) {
        if (movie["_id"] === uid) {
            $('#describeMovieModalLabel').html(movie["name"])
            $('#describeMovieDescription').html(movie["description"])
            $('#describeMovieThumb').html(`<img src="` + movie["thumb"] + `" style="max-width: 207px;max-height: 300px;"/>`)
            $("#describeMovieWatch").attr("onclick", "goto('/watch/movie/" + movie["idv"] + "')");
            $('#describeMovieModal').modal('show')
        }
    })
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