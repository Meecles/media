var auto_hide = true;
function get_alert(color, text){
  //return "<div class='alert alert-" + color + "' role='alert'>" + text + "</div>"
  setTimeout(() => {
    $(".login-text").html("&nbsp;")
  }, 5000);
  return text
}

function login(){
  var username = $("#username").val()
  var password = $("#password").val()
  let redir = $("#redirect").val()
  var host_name = ""
  var toSend = {
    "username": username,
    "password": password,
    "redir": redir
  }
  if (!auto_hide){
    toSend = {
      "mfa_token": $("#mfa_token").val()
    }
  }
  $.ajax({
    url: host_name + "/api/login",
    method: 'POST',
    beforeSend: function(xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", $("#csrf-token").val());
    },
    dataType: "json",
    contentType: "application/json;charset=utf-8",
    data: JSON.stringify(toSend),
    success: function(data) {
      var success = data.success;
      if (success){
          loc = data.redirect
          $(".login-text").html(get_alert("success", "Success!"))
          setTimeout(() => {
            window.location.href = loc
          }, 250);
      }
      else {
          reason = data.reason
          if (reason === "MFA Required"){
            $(".login-text").html("")
            auto_hide = false
            $("#password").val("")
            $("#username").val("")
            var box = "<input type='text' class='form-control form-control-user' id='mfa_token' placeholder='MFA Token' autocomplete='off'>"
            $("#username_box").html(box)
            $("#password_box").html("")
          }
          else {
            alert = get_alert("danger", reason)
            $(".login-text").html(alert)
          }
      }
    }
  });

}

$(document).ready(function() {
  var logout_message = $("#logout_message").val()
  if (logout_message){
    setTimeout(() => {
      $(".login-text").html("&nbsp;")
    }, 5000);
  }
  $("#password").keypress(function(event) {
    if (event.keyCode === 13) {
        $("#login-button").click();
    }
  });
  $("#mfa_token").keypress(function(event) {
    if (event.keyCode === 13) {
        $("#login-button").click();
    }
  });
  $(window).keydown(function(event){
    if(event.keyCode === 13) {
      event.preventDefault();
      $("#login-button").click();
      return false;
    }
  });
});
