async function signup()
{
  url = "/api/createUser"
  var username = document.getElementById("username1").value;
  var password = document.getElementById("password2").value;
  var password_confirm = document.getElementById("password3").value;
  data = {
    "username": username,
    "password": password
  }
  if (password == password_confirm)
  {
    const response = await fetch(url, {
      method: "POST",
      mode: "cors", 
      cache: "no-cache",
      headers: {
        "Content-Type": "application/json",
      },
      redirect: "follow",
      referrerPolicy: "no-referrer",
      body: JSON.stringify(data),
    });
    
    if(response["status"] == 201 || response["status"] == 200)
    {
      alert("Sign Up Successful! Please Login!");
    }else if (response["status"] == 400)
    {
      alert("Missing username or password");
    }else if(response["status"] == 401)
    {
      alert("Username already exists!")
    }else
    {
      alert("Server Error")
    }
  }
  else
  {
    alert("Passwords do not match");
  }
}

async function login()
{
  url = "/api/login"
  var username = document.getElementById("username2").value;
  var password = document.getElementById("password1").value;
  data = {
    "username": username,
    "password": password
  }
 
    const response = await fetch(url, {
      method: "POST",
      mode: "cors", 
      cache: "no-cache",
      headers: {
        "Content-Type": "application/json",
      },
      redirect: "follow",
      referrerPolicy: "no-referrer",
      body: JSON.stringify(data)
    });

    var response_json = await response.json();

    if(response["status"] == 201 || response["status"] == 200)
    {
      alert("Login Successful!");
      //window.location.href = "/"
    }else if(response["status"] == 401)
    {
      alert("Wrong Password or Username")
    }else
    {
      alert("Server Error")
    }
  }
