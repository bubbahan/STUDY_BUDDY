// =============================
// API BASE URL
// =============================

const BASE_URL = "http://127.0.0.1:5000";

// =============================
// HELPERS
// =============================

function getToken() {
    return localStorage.getItem("token");
}

async function apiRequest(endpoint, method = "GET", data = null, auth = false) {
    try {
        const options = {
            method: method,
            headers: {
                "Content-Type": "application/json"
            }
        };

        if (auth) {
            options.headers["Authorization"] = "Bearer " + getToken();
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(BASE_URL + endpoint, options);
        const json = await response.json();
        json._status = response.status;
        json._ok = response.ok;

        // If we get a 401 on an authenticated call, the token is stale — force login
        if (response.status === 401 && auth) {
            localStorage.clear();
            window.location.href = "login.html";
            return json;
        }
        return json;

    } catch (error) {
        console.error("API Error:", error);
        return { _ok: false, message: "Network error" };
    }
}

// =============================
// AUTH APIs
// =============================

function loginAPI(data) {
    return apiRequest("/api/auth/login", "POST", data);
}

function registerAPI(data) {
    return apiRequest("/api/auth/register", "POST", data);
}

// =============================
// DASHBOARD / ANALYTICS
// =============================

function getDashboardData() {
    return apiRequest("/api/analytics/dashboard", "GET", null, true);
}

function getWeakAreas() {
    return apiRequest("/api/analytics/weak-areas", "GET", null, true);
}

// =============================
// TIMETABLE
// =============================

function getTimetable() {
    return apiRequest("/api/timetable", "GET", null, true);
}

function generateTimetable() {
    return apiRequest("/api/timetable/generate", "POST", null, true);
}

// =============================
// STUDY SESSION
// =============================

function saveSession(data) {
    return apiRequest("/api/session", "POST", data, true);
}

function getSessions() {
    return apiRequest("/api/session/all", "GET", null, true);
}

// =============================
// COURSES
// =============================

function getCourses() {
    return apiRequest("/api/courses", "GET", null, true);
}

function enrollCourse(courseId) {
    return apiRequest("/api/courses/enroll/" + courseId, "POST", null, true);
}

function updateCourseProgress(courseId, units) {
    return apiRequest("/api/courses/progress/" + courseId, "POST", { units_completed: units }, true);
}

// =============================
// AUTH GUARD
// =============================

function requireAuth() {
    if (!getToken()) {
        window.location.href = "login.html";
    }
}

// =============================
// LOGOUT
// =============================

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}