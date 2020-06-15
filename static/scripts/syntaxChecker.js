function attachChecker(containerId, btnId) {
    var container = document.getElementById(containerId);
    if(container == null) {
        console.error("Could not attach checker.");
        return;
    }
    var input = container.getElementsByTagName('TEXTAREA')[0];
    var inputHelp = container.getElementsByClassName('input-help')[0];
    var submitButton = document.getElementById(btnId);

    var chk = function(event) {
        reg = /^((\[[^\[\]]*\])+\s*)+$/g
        if(input.value.match(reg) != null) {
            inputHelp.textContent = "Formatare corectă"
            inputHelp.style.color = '#757575';
            submitButton.disabled = false;
        } else {
            inputHelp.textContent = "Formatare incorectă!"
            inputHelp.style.color = '#C62828';
            submitButton.disabled = true;
        }
    }
    chk();
    input.addEventListener("keyup", chk);
}


