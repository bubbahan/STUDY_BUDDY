// =============================
// LOAD TIMETABLE
// =============================

async function loadTimetable() {

    const timetable = await getTimetable();

    const container = document.getElementById("timetableContainer");
    container.innerHTML = "";

    timetable.forEach(item => {

        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <h3>${item.subject}</h3>
            <p>Hours: ${item.hours}</p>
            <p>Time: ${item.time}</p>
        `;

        container.appendChild(div);
    });
}

window.onload = loadTimetable;