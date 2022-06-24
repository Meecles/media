function sort_string(items) {
    return items.sort(
        function (a, b) {
            return a.toLowerCase().localeCompare(b.toLowerCase())
        }
    )
}

function sort_titles(titles) {
    return titles.sort(
        function (a, b) {
            const s = ["The ", "A "];
            s.forEach(function (x) {
                a = a.replace(x, "");
                b = b.replace(x, "");
            })
            return a.toLowerCase().localeCompare(b.toLowerCase())
        }
    )
}

function sort_movies(movies) {
    if (movies.length < 2)
        return movies
    movies = movies.sort(
        function (a0, b0) {
            let a = a0["name"]
            let b = b0["name"]
            const s = ["The ", "A "];
            s.forEach(function (x) {
                a = a.replace(x, "");
                b = b.replace(x, "");
            })
            if (a0.hasOwnProperty("sort_priority") && b0.hasOwnProperty("sort_priority") &&
                a0.hasOwnProperty("year") && b0.hasOwnProperty("year")) {
                let comp_pri = 0
                let comp_year = 0
                if (a0["sort_priority"] < b0["sort_priority"]){
                    comp_pri = -1
                }
                else if (a0["sort_priority"] > b0["sort_priority"]){
                    comp_pri = 1
                }
                if (a0["year"] < b0["year"]){
                    comp_year = -1
                }
                else if (a0["year"] > b0["year"]){
                    comp_year = 1
                }
                return a.toLowerCase().localeCompare(b.toLowerCase()) | comp_year || comp_pri
            }
            return a.toLowerCase().localeCompare(b.toLowerCase())
        }
    )
    return movies
}

function sort_shows(shows) {
    return shows.sort(
        function (a0, b0) {
            let a = a0["name"]
            let b = b0["name"]
            const s = ["The ", "A "];
            s.forEach(function (x) {
                a = a.replace(x, "");
                b = b.replace(x, "");
            })
            return a.toLowerCase().localeCompare(b.toLowerCase())
        }
    )
}
