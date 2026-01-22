// LOGIN FUNCTION
function login() {
    let user = document.getElementById("username").value;
    let pass = document.getElementById("password").value;

    if (user === "" || pass === "") {
        document.getElementById("msg").innerText = "Please fill all fields";
        return;
    }

    // Save login state
    localStorage.setItem("loggedIn", "true");
    localStorage.setItem("username", user);

    window.location.href = "index.html";
}

// CHECK LOGIN
function checkLogin() {
    if (localStorage.getItem("loggedIn") !== "true") {
        window.location.href = "login.html";
    }
}

// SAVE PROFILE
function saveProfile() {
    let profile = {
        name: document.getElementById("name").value,
        age: document.getElementById("age").value,
        height: document.getElementById("height").value,
        weight: document.getElementById("weight").value
    };

    localStorage.setItem("profile", JSON.stringify(profile));
    document.getElementById("status").innerText = "Profile Saved Successfully!";
}

// LOAD PROFILE
function loadProfile() {
    let profile = JSON.parse(localStorage.getItem("profile"));
    if (profile) {
        document.getElementById("name").value = profile.name;
        document.getElementById("age").value = profile.age;
        document.getElementById("height").value = profile.height;
        document.getElementById("weight").value = profile.weight;
    }
}
