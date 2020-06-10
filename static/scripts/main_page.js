function generate_bubble(res) {
    data = JSON.parse(res);
    var lyrics = '';
    if(data.found) {
        lyrics = data.response.text.replace(/\n/g, "<br />");;
        info = '';
        for(i = 0; i < data.song.artists.length; i++) {
            info += data.song.artists[i];
            if(i < data.song.artists.length - 1)
                info += ' x '
        }
        info += ' - ' + data.song.title;
    } else {
        lyrics = '❓❓❓'
        info = 'Cântec negăsit.'
    }
    image = '';
    if(data.response.image) {
        image = `<img src="${data.response.image}"/><div class="overflow"></div>`;
    }
    result = `
    <div class="chat-text-bubble-container">
        <div class="chat-text-bubble">${image}
            <div class="chat-text">${lyrics}</div>
        </div>
        <div class="song-info">${info}</div>
    </div>
    `
    return result;
}

function generate_bubble_sent(text) {
    return `
    <div class="chat-text-bubble-container sent">
        <div class="chat-text-bubble">
            <div class="chat-text">${text}</div>
        </div>
    </div>`
}

function getCompletion(text) {
    if(text == '') return;
    var container = document.getElementById('chatContent');
    var scroller = document.getElementById('chatContentContainer');
    container.innerHTML += generate_bubble_sent(text)
    scroller.scrollTop = scroller.scrollHeight;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this)
            container.innerHTML += generate_bubble(this.response);
            scroller.scrollTop = scroller.scrollHeight;
        }
    };
    xhttp.open("POST", "lyrics", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({query: text}));
}

window.onload = function() {
    var input = document.getElementById('input');
    var sendButton = document.getElementById('sendButton');
    input.addEventListener("keyup", function(event) {
      if (event.keyCode === 13) {
        event.preventDefault();
        getCompletion(event.target.value)
        event.target.value = '';
      }
    });
    sendButton.addEventListener("click", function(event) {
        getCompletion(input.value)
        input.value = '';
    });

    var infoScreen = document.getElementById('infoScreen');
    var infoButton = document.getElementById('infoButton');
    var infoCloseButton = document.getElementById('infoCloseButton');
    infoButton.addEventListener("click", function(event) {
        infoScreen.classList.add('open');
    });
    infoCloseButton.addEventListener("click", function(event) {
        infoScreen.classList.remove('open');
    });
}