function createToast(message, timeout) {
    var toastArea = document.getElementById("toastArea");
    var toast = document.createElement("div");
    toast.className = 'toast';
    toast.innerText = message;
    toastArea.appendChild(toast);
    setTimeout(function() {
        toast.className = 'toast opened'
    }, 1)
    setTimeout(function() {
        toast.className = 'toast'
        setTimeout(function() {
            toast.remove();
        }, 200)
    }, timeout)
}