var name_patten = new RegExp(/^[\u4E00-\u9FA5\uF900-\uFA2D\w-]{3,19}$/);
var email_patten = new RegExp(/^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-]{2,})+/);
var phone_patten = new RegExp(/^1[345678]\d{9}$/);
var pwd_patten = new RegExp(/^[_\w-]{6,29}$/);
function check_patten() {
    var name_value=document.getElementById("username").value;
    var checkName = true;
    var checkEmail = true;
    var checkPhone = true;
    var checkPwd = true;
    if(name_patten.test(name_value)){
        checkEmail=false;
        checkPhone=false;
    }
    else if(email_patten.test(name_value)){
        checkName=false;
        checkPhone=false;
    }
    else if(phone_patten.test(name_mvalue)){
        checkName=false;
        checkEmail=false;
    }
    else if(pwd_patten.test()){

    }
}

