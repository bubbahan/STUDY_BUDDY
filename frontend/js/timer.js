let timerInterval;
let seconds = 0;
let running = false;

// =============================
// FORMAT TIME
// =============================
function formatTime(sec) {
    let hrs = Math.floor(sec / 3600);
    let mins = Math.floor((sec % 3600) / 60);
    let secs = sec % 60;
    return `${hrs}:${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

// =============================
// START TIMER
// =============================
function startTimer() {
    if (running) return;
    running = true;
    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = false;

    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById("timerDisplay").innerText = formatTime(seconds);
    }, 1000);
}

// =============================
// STOP TIMER
// =============================
function stopTimer() {
    running = false;
    clearInterval(timerInterval);
    document.getElementById("startBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;
}

// =============================
// RESET TIMER
// =============================
function resetTimer() {
    stopTimer();
    seconds = 0;
    document.getElementById("timerDisplay").innerText = "0:00:00";
}

// =============================
// SAVE SESSION (API-wired)
// =============================
async function saveStudySession() {
    const subject = document.getElementById("subject").value.trim();
    const plannedHours = parseFloat(document.getElementById("plannedHours").value) || 0;
    const unitsCompleted = parseInt(document.getElementById("unitsCompleted").value) || 0;
    const msgEl = document.getElementById("sessionMsg");

    if (!subject) {
        msgEl.style.color = "red";
        msgEl.innerText = "Please enter a subject name.";
        return;
    }

    if (seconds < 5) {
        msgEl.style.color = "red";
        msgEl.innerText = "Please run the timer for at least a few seconds before saving.";
        return;
    }

    // Convert seconds to hours, round to 2 decimal places
    const actualHours = parseFloat((seconds / 3600).toFixed(2));

    const saveBtn = document.getElementById("saveBtn");
    saveBtn.disabled = true;
    msgEl.style.color = "#333";
    msgEl.innerText = "Saving...";

    const response = await saveSession({
        subject: subject,
        planned_time: plannedHours,
        actual_time: actualHours,
        unit_completed: unitsCompleted
    });

    if (response._ok) {
        // Show XP feedback if returned from backend
        let msg = "✅ Session saved! Keep it up!";
        if (response.xp_earned) {
            msg += ` +${Math.round(response.xp_earned)} XP`;
        }
        if (response.level) {
            // Update cached level
            localStorage.setItem("level", response.level);
            localStorage.setItem("xp", response.xp);
        }
        msgEl.style.color = "#28a745";
        msgEl.innerText = msg;

        // Reset form
        resetTimer();
        document.getElementById("subject").value = "";
        document.getElementById("plannedHours").value = "";
        document.getElementById("unitsCompleted").value = "";
    } else {
        msgEl.style.color = "red";
        msgEl.innerText = "❌ " + (response.message || "Failed to save session.");
    }

    saveBtn.disabled = false;
}

requireAuth();