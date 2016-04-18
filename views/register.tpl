%from bottle import url
<!DOCTYPE html>
<html >
  <head>
    <meta charset="UTF-8">
    <title>login page</title>
    <link rel="stylesheet" type="text/css" href="{{ url("static", filename='login.css') }}">
    <script src="{{ url("static", filename='jquery-1.6.2.min.js') }}" type="text/javascript"></script>
    <script src="{{ url("static", filename='register.js') }}" type="text/javascript"></script>       
  </head>

  <body>

    
<form action="/register" method="post" id="registerform">
  <header>Register</header>
  <label>Username</label>
  <input name="username" type="text" value="{{login_text}}" onfocus="if (this.value=='{{login_text}}') this.value='';"/>
  <div class="help">At least 7 character</div>
  <label>Password</label>
  <input name="password" type="password" />
  <div class="help">Use upper and lowercase lettes and numbers</div>
  <button class ="register" type="submit">Register</button>
</form>

  </body>
</html>
