// =============================
// LOAD DASHBOARD
// =============================

async function loadDashboard() {

    const data = await getDashboardData();

    document.getElementById("daysRemaining").innerText = data.days_remaining;
    document.getElementById("prepPercent").innerText = data.preparation + "%";
    document.getElementById("streak").innerText = data.streak;

}

// Load when page opens
window.onload = loadDashboard;