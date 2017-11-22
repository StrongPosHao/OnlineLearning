function checkInput() {
    var password_input=document.getElementById('password');
    var password_md5=document.getElementById('password_md5');
    password_md5.value=md5(password_input.value);
    return true;
}