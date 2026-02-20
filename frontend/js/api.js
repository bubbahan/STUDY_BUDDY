// =============================
// API BASE URL
// =============================

const BASE_URL = "http://127.0.0.1:5000";

// =============================
// GENERIC REQUEST FUNCTION
// =============================

async function apiRequest(endpoint, method = "GET", data = null) {
    try {
        const options = {
            method: method,
            headers: {
                "Content-Type": "application/json"
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(BASE_URL + endpoint, options);
        return await response.json();

    } catch (error) {
        console.error("API Error:", error);
    }
}

// =============================
// AUTH APIs
// =============================

function loginAPI(data) {
    return apiRequest("/login", "POST", data);
}

function registerAPI(data) {
    return apiRequest("/register", "POST", data);
}

// =============================
// DASHBOARD
// =============================

function getDashboardData() {
    return apiRequest("/dashboard");
}

// =============================
// TIMETABLE
// =============================

function getTimetable() {
    return apiRequest("/timetable");
}

// =============================
// TIMER SESSION
// =============================

function saveSession(data) {
    return apiRequest("/session", "POST", data);
}