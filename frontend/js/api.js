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

// Multipart (for file uploads — no JSON Content-Type)
async function apiUpload(endpoint, formData) {
    try {
        const response = await fetch(BASE_URL + endpoint, {
            method: "POST",
            headers: { "Authorization": "Bearer " + getToken() },
            body: formData
        });
        const json = await response.json();
        json._ok = response.ok;
        return json;
    } catch (e) {
        return { _ok: false, message: "Upload error" };
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
// SUBJECTS (with new fields)
// =============================

function getSubjects() {
    return apiRequest("/api/subjects/", "GET", null, true);
}

function getSubject(id) {
    return apiRequest(`/api/subjects/${id}`, "GET", null, true);
}

function addSubject(data) {
    return apiRequest("/api/subjects/", "POST", data, true);
}

function updateSubject(id, data) {
    return apiRequest(`/api/subjects/${id}`, "PUT", data, true);
}

function deleteSubject(id) {
    return apiRequest(`/api/subjects/${id}`, "DELETE", null, true);
}

// =============================
// SYLLABUS
// =============================

function getSyllabus(subjectId) {
    return apiRequest(`/api/syllabus/${subjectId}`, "GET", null, true);
}

function addTopic(subjectId, topicName) {
    return apiRequest(`/api/syllabus/${subjectId}`, "POST", { topic_name: topicName }, true);
}

function toggleTopic(topicId) {
    return apiRequest(`/api/syllabus/${topicId}/toggle`, "PUT", null, true);
}

function deleteTopic(topicId) {
    return apiRequest(`/api/syllabus/${topicId}`, "DELETE", null, true);
}

// =============================
// USER / SETTINGS
// =============================

function uploadPhoto(formData) {
    return apiUpload("/api/user/upload-photo", formData);
}

function saveAlarmSound(sound) {
    return apiRequest("/api/user/update", "PUT", { alarm_sound: sound }, true);
}

function getProfile() {
    return apiRequest("/api/user/profile", "GET", null, true);
}

// =============================
// COURSES (legacy — redirects to subjects)
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

// =============================
// AI API
// =============================

function getAITimetable() {
    return apiRequest("/api/ai/timetable", "POST", null, true);
}

function getAITips() {
    return apiRequest("/api/ai/tips", "POST", null, true);
}