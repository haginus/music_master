function add_song(req) {
    var submitButton = document.getElementById('submit');
    submitButton.disabled = true;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
                var res = JSON.parse(this.response);
                if(res.success) {
                    createToast("Piesă salvată.", 3000);
                    setTimeout(function() {
                        window.location.replace(`${window.location.origin}/admin/songs/edit/${res.song_id}`);
                    }, 1000);
                }
            }
    };
    xhttp.open("POST", "/admin/songs/add", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(req));
}

function edit_song(req) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var res = JSON.parse(this.response);
                if(res.success) {
                    createToast("Piesă salvată.", 3000);
                }
            }
        };
        xhttp.open("POST", "/admin/songs/edit", true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify(req));
    }

window.onload = function() {
    attachChecker("checkField", "submit");
    var submitButton = document.getElementById('submit');
    submitButton.addEventListener("click", function(event) {
        event.preventDefault();
        var title = document.getElementById('songTitle').value
        var artists = document.getElementById('songArtists').value.split(', ')
        var lyrics = document.getElementById('songLyrics').value
        if(submitButton.getAttribute("data-action") == 'edit') {
            var id = document.getElementById('songId').value
            edit_song({'id': id, 'title': title, 'artists': artists, 'lyrics': lyrics});
        }
        else if(submitButton.getAttribute("data-action") == 'add')
            add_song({'title': title, 'artists': artists, 'lyrics': lyrics});
    });
}