// LOGIN FUNCTION
function login() {
    let user = document.getElementById("username").value;
    let pass = document.getElementById("password").value;

    if (user === "" || pass === "") {
        document.getElementById("msg").innerText = "All fields required";
        return;
    }

    if (pass.length < 6) {
        document.getElementById("msg").innerText = "Password must be at least 6 characters";
        return;
    }

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

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}
function showDashboardProfile() {
    let profile = JSON.parse(localStorage.getItem("profile"));
    let user = localStorage.getItem("username");

    if (profile) {
        document.getElementById("userInfo").innerHTML =
            "Name: " + profile.name + "<br>" +
            "Age: " + profile.age + "<br>" +
            "Height: " + profile.height + " cm<br>" +
            "Weight: " + profile.weight + " kg";
    } else {
        document.getElementById("userInfo").innerText =
            "Welcome " + user + ", please update your profile.";
    }
}
function saveFitness() {
    let data = {
        workout: document.getElementById("workout").value,
        calories: document.getElementById("caloriesBurned").value
    };

    localStorage.setItem("fitness", JSON.stringify(data));
    document.getElementById("fitMsg").innerText = "Fitness data saved!";
}
function saveDiet() {
    let data = {
        meal: document.getElementById("meal").value,
        calories: document.getElementById("caloriesIntake").value
    };

    localStorage.setItem("diet", JSON.stringify(data));
    document.getElementById("dietMsg").innerText = "Diet data saved!";
}
