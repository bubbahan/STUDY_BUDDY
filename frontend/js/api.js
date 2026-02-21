// =============================
// API BASE URL
// =============================

const BASE_URL = "";

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

        // If we get a 401/422 on an authenticated call, the token is stale — force login
        if ((response.status === 401 || response.status === 422) && auth) {
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
// COURSES (legacy)
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

// =============================
// SOUND MANAGER (WEB AUDIO API)
// =============================
const SoundManager = {
    audioCtx: null,
    activeOscillators: [],
    loopIntervals: [],

    init() {
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
    },

    play(soundName, loop = false) {
        this.init();
        if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }
        this.stop();

        switch (soundName) {
            case 'chime': this._playChime(loop); break;
            case 'classic': this._playClassic(loop); break;
            case 'digital': this._playDigital(loop); break;
            case 'nature': this._playNature(loop); break;
            default: this._playDefault(loop); break;
        }
    },

    stop() {
        this.activeOscillators.forEach(node => {
            try { node.stop(); } catch (e) { }
            try { node.disconnect(); } catch (e) { }
        });
        this.activeOscillators = [];
        this.loopIntervals.forEach(id => clearInterval(id));
        this.loopIntervals = [];
    },

    _createGain(duration, volume = 0.1) {
        const gain = this.audioCtx.createGain();
        gain.gain.setValueAtTime(volume, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.audioCtx.currentTime + duration);
        gain.connect(this.audioCtx.destination);
        return gain;
    },

    _playDefault(loop) {
        const playOnce = () => {
            const osc = this.audioCtx.createOscillator();
            const gain = this._createGain(0.5);
            osc.frequency.setValueAtTime(880, this.audioCtx.currentTime);
            osc.connect(gain); osc.start(); osc.stop(this.audioCtx.currentTime + 0.5);
            this.activeOscillators.push(osc);
        };
        playOnce();
        if (loop) this.loopIntervals.push(setInterval(playOnce, 1000));
    },

    _playChime(loop) {
        const playOnce = () => {
            [440, 554, 659].forEach((freq, i) => {
                const osc = this.audioCtx.createOscillator();
                const gain = this._createGain(1.5, 0.05);
                osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime + (i * 0.1));
                osc.connect(gain); osc.start(this.audioCtx.currentTime + (i * 0.1));
                osc.stop(this.audioCtx.currentTime + 1.5);
                this.activeOscillators.push(osc);
            });
        };
        playOnce();
        if (loop) this.loopIntervals.push(setInterval(playOnce, 2000));
    },

    _playClassic(loop) {
        const playOnce = () => {
            for (let i = 0; i < 4; i++) {
                const osc = this.audioCtx.createOscillator();
                const gain = this.audioCtx.createGain();
                gain.gain.setValueAtTime(0.1, this.audioCtx.currentTime + (i * 0.2));
                gain.gain.setValueAtTime(0, this.audioCtx.currentTime + (i * 0.2) + 0.1);
                gain.connect(this.audioCtx.destination);
                osc.type = 'square'; osc.frequency.setValueAtTime(600, this.audioCtx.currentTime);
                osc.connect(gain); osc.start(this.audioCtx.currentTime + (i * 0.2));
                osc.stop(this.audioCtx.currentTime + (i * 0.2) + 0.15);
                this.activeOscillators.push(osc);
            }
        };
        playOnce();
        if (loop) this.loopIntervals.push(setInterval(playOnce, 1000));
    },

    _playDigital(loop) {
        const playOnce = () => {
            const osc = this.audioCtx.createOscillator();
            const gain = this._createGain(0.1, 0.1);
            osc.type = 'triangle'; osc.frequency.setValueAtTime(2000, this.audioCtx.currentTime);
            osc.connect(gain); osc.start(); osc.stop(this.audioCtx.currentTime + 0.1);
            this.activeOscillators.push(osc);
        };
        playOnce();
        if (loop) this.loopIntervals.push(setInterval(playOnce, 150));
    },

    _playNature(loop) {
        const bufferSize = 2 * this.audioCtx.sampleRate,
            noiseBuffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate),
            output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) output[i] = Math.random() * 2 - 1;
        const whiteNoise = this.audioCtx.createBufferSource();
        whiteNoise.buffer = noiseBuffer; whiteNoise.loop = loop;
        const filter = this.audioCtx.createBiquadFilter();
        filter.type = 'lowpass'; filter.frequency.value = 400;
        const gain = this.audioCtx.createGain(); gain.gain.value = 0.05;
        whiteNoise.connect(filter); filter.connect(gain); gain.connect(this.audioCtx.destination);
        whiteNoise.start(); this.activeOscillators.push(whiteNoise);
    }
};