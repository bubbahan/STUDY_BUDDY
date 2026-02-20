// =============================
// LOGIN
// =============================

async function loginUser() {

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await loginAPI({
        email: email,
        password: password
    });

    if (response.message === "Login successful") {
        alert("Login Success");
        window.location.href = "dashboard.html";
    } else {
        alert("Invalid Credentials");
    }
}

// =============================
// REGISTER
// =============================

async function registerUser() {

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await registerAPI({
        name,
        email,
        password
    });

    if (response.message === "User registered") {
        alert("Registration Success");
        window.location.href = "login.html";
    } else {
        alert("Error registering");
    }
}