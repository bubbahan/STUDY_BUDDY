let timer;
let seconds = 0;
let running = false;

// =============================
// FORMAT TIME
// =============================

function formatTime(sec) {

    let hrs = Math.floor(sec / 3600);
    let mins = Math.floor((sec % 3600) / 60);
    let secs = sec % 60;

    return `${hrs}:${mins}:${secs}`;
}

// =============================
// START TIMER
// =============================

function startTimer() {

    if (running) return;

    running = true;

    timer = setInterval(() => {
        seconds++;
        document.getElementById("timerDisplay").innerText = formatTime(seconds);
    }, 1000);
}

// =============================
// STOP TIMER
// =============================

function stopTimer() {

    running = false;
    clearInterval(timer);
}

// =============================
// RESET TIMER
// =============================

function resetTimer() {

    stopTimer();
    seconds = 0;
    document.getElementById("timerDisplay").innerText = "0:0:0";
}

// =============================
// SAVE SESSION
// =============================

async function saveStudySession() {

    const subject = document.getElementById("subject").value;

    const response = await saveSession({
        subject: subject,
        duration: seconds
    });

    alert("Session Saved");

    resetTimer();
}