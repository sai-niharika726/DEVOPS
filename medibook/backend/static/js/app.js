const API = "";

let state = {
  token: localStorage.getItem("mb_token") || null,
  user: JSON.parse(localStorage.getItem("mb_user") || "null"),
  selectedSlotId: null,
  selectedDoctorName: null,
};

async function api(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && state.token) headers["Authorization"] = `Bearer ${state.token}`;
  const res = await fetch(`${API}${path}`, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function setSession(token, user) {
  state.token = token; state.user = user;
  localStorage.setItem("mb_token", token);
  localStorage.setItem("mb_user", JSON.stringify(user));
  renderAuthState();
}
function clearSession() {
  state.token = null; state.user = null;
  localStorage.removeItem("mb_token"); localStorage.removeItem("mb_user");
  renderAuthState();
}

function renderAuthState() {
  const loggedIn = !!state.user;
  document.getElementById("auth-area").hidden = loggedIn;
  document.getElementById("user-area").hidden = !loggedIn;
  if (loggedIn) document.getElementById("user-name").textContent = `${state.user.name} (${state.user.role})`;

  document.getElementById("nav-appointments").hidden = !(loggedIn && state.user.role === "patient");
  document.getElementById("nav-add-doctor").hidden = !(loggedIn && state.user.role === "doctor");
}

function showView(view) {
  document.querySelectorAll(".view").forEach(v => v.hidden = true);
  document.getElementById(`view-${view}`).hidden = false;
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.toggle("active", b.dataset.view === view));
  if (view === "browse") { loadStats(); loadDoctors(); }
  if (view === "appointments") loadAppointments();
}

document.querySelector(".nav-links").addEventListener("click", e => {
  if (e.target.matches(".nav-btn")) showView(e.target.dataset.view);
});

async function loadStats() {
  try {
    const s = await api("/api/doctors/stats");
    document.getElementById("stats-bar").innerHTML = `
      <div class="stat-card"><div class="label">Available doctors</div><div class="value">${s.available_doctors}</div></div>
      <div class="stat-card"><div class="label">Specialities</div><div class="value">${s.specialities}</div></div>
      <div class="stat-card"><div class="label">Total appointments</div><div class="value">${s.total_appointments}</div></div>
      <div class="stat-card"><div class="label">Patients served</div><div class="value">${s.total_patients}</div></div>
    `;
  } catch(e) { console.error(e); }
}

async function loadDoctors() {
  const list = document.getElementById("doctors-list");
  list.innerHTML = "<p>Loading…</p>";
  const spec = document.getElementById("speciality-filter").value;
  try {
    const doctors = await api(`/api/doctors${spec ? "?speciality=" + spec : ""}`);
    if (!doctors.length) { list.innerHTML = "<p>No doctors found.</p>"; return; }
    list.innerHTML = doctors.map(d => `
      <div class="doctor-card">
        <div class="avatar">${d.name.split(" ").map(n=>n[0]).join("").slice(0,2)}</div>
        <h3>${d.name}</h3>
        <p>${d.speciality} · ${d.experience_years} yrs exp</p>
        ${d.bio ? `<p style="margin-top:6px;font-size:12px;color:#888780;">${d.bio}</p>` : ""}
        <span class="badge ${d.available ? "" : "unavailable"}">${d.available ? "Available" : "Unavailable"}</span>
        ${state.user?.role === "patient" ? `<div style="margin-top:10px;"><button class="btn-primary" style="font-size:12px;padding:6px 12px;" data-book="${d.id}" data-name="${d.name}">Book slot</button></div>` : ""}
      </div>
    `).join("");
    list.querySelectorAll("[data-book]").forEach(btn => {
      btn.addEventListener("click", () => openSlotModal(btn.dataset.book, btn.dataset.name));
    });
    await loadSpecialityFilter();
  } catch(e) { list.innerHTML = `<p>Error: ${e.message}</p>`; }
}

async function loadSpecialityFilter() {
  try {
    const specs = await api("/api/doctors/specialities");
    const sel = document.getElementById("speciality-filter");
    const current = sel.value;
    sel.innerHTML = `<option value="">All specialities</option>` + specs.map(s => `<option value="${s}" ${s===current?"selected":""}>${s}</option>`).join("");
  } catch(e) {}
}
document.getElementById("speciality-filter").addEventListener("change", loadDoctors);

async function openSlotModal(doctorId, doctorName) {
  if (!state.user) { openModal("login"); return; }
  state.selectedDoctorName = doctorName;
  document.getElementById("slot-modal-title").textContent = `Book with ${doctorName}`;
  document.getElementById("slot-msg").textContent = "";
  document.getElementById("slot-reason").value = "";
  state.selectedSlotId = null;

  const slotsList = document.getElementById("slots-list");
  slotsList.innerHTML = "<p>Loading slots…</p>";
  document.getElementById("slot-modal").hidden = false;

  try {
    const slots = await api(`/api/doctors/${doctorId}/slots`);
    if (!slots.length) { slotsList.innerHTML = "<p>No available slots.</p>"; return; }
    slotsList.innerHTML = slots.map(s => `
      <div class="slot-item" id="slot-${s.id}">
        <span>${s.slot_date} at ${s.slot_time}</span>
        <button class="btn-ghost" style="font-size:12px;" data-slot="${s.id}">Select</button>
      </div>
    `).join("");
    slotsList.querySelectorAll("[data-slot]").forEach(btn => {
      btn.addEventListener("click", () => {
        slotsList.querySelectorAll(".slot-item").forEach(el => el.style.border = "1px solid #e3e1d8");
        document.getElementById(`slot-${btn.dataset.slot}`).style.border = "2px solid #185fa5";
        state.selectedSlotId = btn.dataset.slot;
      });
    });
  } catch(e) { slotsList.innerHTML = `<p>Error: ${e.message}</p>`; }
}
document.getElementById("close-slot-modal").addEventListener("click", () => {
  document.getElementById("slot-modal").hidden = true;
});
document.getElementById("confirm-booking-btn").addEventListener("click", async () => {
  const msg = document.getElementById("slot-msg");
  if (!state.selectedSlotId) { msg.textContent = "Please select a slot first."; return; }
  try {
    await api("/api/appointments", {
      method: "POST", auth: true,
      body: { slot_id: parseInt(state.selectedSlotId), reason: document.getElementById("slot-reason").value },
    });
    msg.style.color = "#27500a";
    msg.textContent = "Appointment booked!";
    setTimeout(() => { document.getElementById("slot-modal").hidden = true; loadStats(); }, 1200);
  } catch(e) { msg.style.color = "#993c1d"; msg.textContent = e.message; }
});

async function loadAppointments() {
  const list = document.getElementById("appointments-list");
  list.innerHTML = "<p>Loading…</p>";
  try {
    const appts = await api("/api/appointments/mine", { auth: true });
    if (!appts.length) { list.innerHTML = "<p>No appointments yet.</p>"; return; }
    list.innerHTML = appts.map(a => `
      <div class="appt-card">
        <h3>Dr. ${a.doctor}</h3>
        <p>${a.speciality}</p>
        <p>${a.slot_date} at ${a.slot_time}</p>
        ${a.reason ? `<p style="margin-top:6px;font-size:12px;color:#888780;">${a.reason}</p>` : ""}
        <span class="status-badge status-${a.status}">${a.status}</span>
        ${a.status === "booked" ? `<div style="margin-top:10px;"><button class="btn-ghost" style="font-size:12px;" data-cancel="${a.id}">Cancel</button></div>` : ""}
      </div>
    `).join("");
    list.querySelectorAll("[data-cancel]").forEach(btn => {
      btn.addEventListener("click", async () => {
        try {
          await api(`/api/appointments/${btn.dataset.cancel}/cancel`, { method: "PATCH", auth: true });
          loadAppointments(); loadStats();
        } catch(e) { alert(e.message); }
      });
    });
  } catch(e) { list.innerHTML = `<p>Error: ${e.message}</p>`; }
}

document.getElementById("doctor-form").addEventListener("submit", async e => {
  e.preventDefault();
  const msg = document.getElementById("doctor-msg");
  try {
    await api("/api/doctors", {
      method: "POST", auth: true,
      body: {
        speciality: document.getElementById("d-speciality").value,
        experience_years: parseInt(document.getElementById("d-exp").value),
        bio: document.getElementById("d-bio").value,
      },
    });
    msg.style.color = "#27500a"; msg.textContent = "Profile created!";
    e.target.reset();
  } catch(e) { msg.style.color = "#993c1d"; msg.textContent = e.message; }
});

const authModal = document.getElementById("auth-modal");
function openModal(tab) { authModal.hidden = false; switchTab(tab); }
document.getElementById("login-btn").addEventListener("click", () => openModal("login"));
document.getElementById("register-btn").addEventListener("click", () => openModal("register"));
document.getElementById("close-modal").addEventListener("click", () => authModal.hidden = true);
function switchTab(tab) {
  document.getElementById("tab-login").classList.toggle("active", tab === "login");
  document.getElementById("tab-register").classList.toggle("active", tab === "register");
  document.getElementById("login-form").hidden = tab !== "login";
  document.getElementById("register-form").hidden = tab !== "register";
}
document.getElementById("tab-login").addEventListener("click", () => switchTab("login"));
document.getElementById("tab-register").addEventListener("click", () => switchTab("register"));

document.getElementById("login-form").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: { email: document.getElementById("login-email").value, password: document.getElementById("login-password").value },
    });
    setSession(data.token, data.user); authModal.hidden = true; showView("browse");
  } catch(e) { document.getElementById("login-msg").textContent = e.message; }
});

document.getElementById("register-form").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    const data = await api("/api/auth/register", {
      method: "POST",
      body: {
        name: document.getElementById("reg-name").value,
        email: document.getElementById("reg-email").value,
        password: document.getElementById("reg-password").value,
        role: document.getElementById("reg-role").value,
      },
    });
    setSession(data.token, data.user); authModal.hidden = true; showView("browse");
  } catch(e) { document.getElementById("register-msg").textContent = e.message; }
});

document.getElementById("logout-btn").addEventListener("click", () => { clearSession(); showView("browse"); });

renderAuthState();
loadStats();
loadDoctors();
