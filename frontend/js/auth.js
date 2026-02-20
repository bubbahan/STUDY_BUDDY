// =============================
// LOGIN
// =============================

async function loginUser() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const errorEl = document.getElementById("errorMsg");

    if (!email || !password) {
        if (errorEl) errorEl.innerText = "Please fill in all fields.";
        return;
    }

    const response = await loginAPI({ email, password });

    if (response._ok && response.token) {
        localStorage.setItem("token", response.token);
        localStorage.setItem("name", response.name);
        localStorage.setItem("level", response.level);
        localStorage.setItem("xp", response.xp);
        window.location.href = "dashboard.html";
    } else {
        const msg = response.message || "Invalid credentials";
        if (errorEl) errorEl.innerText = msg;
        else alert(msg);
    }
}

// =============================
// REGISTER
// =============================

async function registerUser() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const hours = parseInt(document.getElementById("hours").value) || 4;
    const sleep = document.getElementById("sleep").value || "23:00";
    const wake = document.getElementById("wake").value || "07:00";
    const exam = document.getElementById("exam").value || null;
    const prefEl = document.getElementById("preference");
    const preference = prefEl ? prefEl.value : "morning";
    const subjectsEl = document.getElementById("subjects");
    const subjectsRaw = subjectsEl ? subjectsEl.value : "";
    const subjects = subjectsRaw.split(",").map(s => s.trim()).filter(Boolean);

    const errorEl = document.getElementById("errorMsg");

    if (!name || !email || !password) {
        if (errorEl) errorEl.innerText = "Name, email, and password are required.";
        else alert("Name, email, and password are required.");
        return;
    }

    const response = await registerAPI({
        name,
        email,
        password,
        study_hours_per_day: hours,
        sleep_time: sleep,
        wake_time: wake,
        exam_date: exam,
        preference,
        subjects
    });

    if (response._ok) {
        alert("Registration successful! Please log in.");
        window.location.href = "login.html";
    } else {
        const msg = response.message || "Registration failed.";
        if (errorEl) errorEl.innerText = msg;
        else alert(msg);
    }
}