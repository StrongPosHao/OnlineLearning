function resure_password() {
    var pwd1=document.getElementById("password1");
    var pwd2=document.getElementById("password2");
    if(pwd1.value!=pwd2.value){
        pwd1.setCustomValidity("not pass");
    }
    else{
        pwd1.setCustomValidity("");
    }
};
