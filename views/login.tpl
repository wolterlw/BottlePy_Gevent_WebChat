%from bottle import url
<!DOCTYPE html>
<html >
  <head>
    <meta charset="UTF-8">
    <title>login page</title>
    <link rel="stylesheet" type="text/css" href="{{ url("static", filename='login.css') }}">
    <script src="{{ url("static", filename='login.js') }}" type="text/javascript"></script>   
    <script src="{{ url("static", filename='jquery-1.6.2.min.js') }}" type="text/javascript"></script>
  </head>

  <body>

    
<form action="/login" method="post" id="loginform">
  <header>Login</header>
  <label>Username</label>
  <input name="username" type="text" />
  <div class="help">At least 7 character</div>
  <label>Password</label>
  <input name="password" type="password" />
  <div class="help">Use upper and lowercase lettes as well</div>
  <table>
  <td><button class="login" type="submit">Login</button></td>
  <td><button class="register" type="button" onclick="newRegister()">Register</button></td>
  </table>
</form>    
  </body>
</html>
