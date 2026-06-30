const API_BASE = window.API_BASE_URL || "/api";

let state = {
  token: localStorage.getItem("fb_token") || null,
  user: JSON.parse(localStorage.getItem("fb_user") || "null"),
};

// ---------- API helpers ----------
async function api(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && state.token) headers["Authorization"] = `Bearer ${state.token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

// ---------- Auth ----------
function setSession(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem("fb_token", token);
  localStorage.setItem("fb_user", JSON.stringify(user));
  renderAuthState();
}

function clearSession() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("fb_token");
  localStorage.removeItem("fb_user");
  renderAuthState();
}

function renderAuthState() {
  const loggedIn = !!state.user;
  document.getElementById("auth-area").hidden = loggedIn;
  document.getElementById("user-area").hidden = !loggedIn;

  if (loggedIn) {
    document.getElementById("user-name").textContent =
      `${state.user.name} (${state.user.role})`;
  }

  document.querySelector(".nav-btn[data-view='post']").hidden =
    !(loggedIn && state.user.role === "donor");
  document.querySelector(".nav-btn[data-view='claims']").hidden =
    !(loggedIn && state.user.role === "volunteer");
}

// ---------- View switching ----------
function showView(view) {
  document.querySelectorAll(".view").forEach((v) => (v.hidden = true));
  document.getElementById(`view-${view}`).hidden = false;
  document.querySelectorAll(".nav-btn").forEach((b) =>
    b.classList.toggle("active", b.dataset.view === view)
  );
  if (view === "browse") loadDonations();
  if (view === "claims") loadClaims();
}

document.getElementById("nav-links").addEventListener("click", (e) => {
  if (e.target.matches(".nav-btn")) showView(e.target.dataset.view);
});

// ---------- Stats ----------
async function loadStats() {
  try {
    const stats = await api("/donations/stats");
    document.getElementById("stats-bar").innerHTML = `
      <div class="stat-card"><div class="label">Active listings</div><div class="value">${stats.active_listings}</div></div>
      <div class="stat-card"><div class="label">Completed donations</div><div class="value">${stats.completed_donations}</div></div>
      <div class="stat-card"><div class="label">Donors</div><div class="value">${stats.donors}</div></div>
      <div class="stat-card"><div class="label">Volunteers</div><div class="value">${stats.volunteers}</div></div>
    `;
  } catch (err) {
    console.error(err);
  }
}

// ---------- Donations ----------
async function loadDonations() {
  const list = document.getElementById("donations-list");
  list.innerHTML = "<p>Loading…</p>";
  try {
    const donations = await api("/donations?status=available");
    if (!donations.length) {
      list.innerHTML = "<p>No donations available right now.</p>";
      return;
    }
    list.innerHTML = donations.map(donationCard).join("");
    list.querySelectorAll("[data-claim-id]").forEach((btn) => {
      btn.addEventListener("click", () => claimDonation(btn.dataset.claimId));
    });
  } catch (err) {
    list.innerHTML = `<p>Could not load donations: ${err.message}</p>`;
  }
}

function donationCard(d) {
  const deadline = new Date(d.pickup_deadline).toLocaleString();
  const canClaim = state.user && state.user.role === "volunteer";
  return `
    <div class="donation-card">
      <h3>${d.title}</h3>
      <p>${d.quantity} · ${d.pickup_location}</p>
      <p>Pickup by ${deadline}</p>
      ${d.donor?.org_name ? `<p>From ${d.donor.org_name}</p>` : ""}
      <span class="badge">${d.food_type.replace("_", "-")}</span>
      ${canClaim ? `<div style="margin-top:10px;"><button class="btn-primary" data-claim-id="${d.id}">Claim</button></div>` : ""}
    </div>
  `;
}

async function claimDonation(id) {
  try {
    await api(`/donations/${id}/claim`, { method: "POST", auth: true });
    loadDonations();
    loadStats();
  } catch (err) {
    alert(err.message);
  }
}

document.getElementById("post-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("post-message");
  try {
    await api("/donations", {
      method: "POST",
      auth: true,
      body: {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        quantity: document.getElementById("quantity").value,
        food_type: document.getElementById("food_type").value,
        pickup_location: document.getElementById("pickup_location").value,
        pickup_deadline: document.getElementById("pickup_deadline").value,
      },
    });
    msg.style.color = "#27500a";
    msg.textContent = "Listing posted.";
    e.target.reset();
    loadStats();
  } catch (err) {
    msg.style.color = "#993c1d";
    msg.textContent = err.message;
  }
});

// ---------- Claims ----------
async function loadClaims() {
  const list = document.getElementById("claims-list");
  list.innerHTML = "<p>Loading…</p>";
  try {
    const claims = await api("/donations/claims/mine", { auth: true });
    if (!claims.length) {
      list.innerHTML = "<p>You haven't claimed anything yet.</p>";
      return;
    }
    list.innerHTML = claims.map((c) => `
      <div class="donation-card">
        <h3>${c.donation.title}</h3>
        <p>${c.donation.quantity} · ${c.donation.pickup_location}</p>
        <span class="badge claimed">${c.status}</span>
        ${c.status === "claimed" ? `
          <div style="margin-top:10px; display:flex; gap:8px;">
            <button class="btn-primary" data-status="completed" data-claim="${c.id}">Mark completed</button>
            <button class="btn-ghost" data-status="cancelled" data-claim="${c.id}">Cancel</button>
          </div>` : ""}
      </div>
    `).join("");
    list.querySelectorAll("[data-status]").forEach((btn) => {
      btn.addEventListener("click", () => updateClaim(btn.dataset.claim, btn.dataset.status));
    });
  } catch (err) {
    list.innerHTML = `<p>Could not load claims: ${err.message}</p>`;
  }
}

async function updateClaim(claimId, status) {
  try {
    await api(`/donations/claims/${claimId}/status`, {
      method: "PATCH",
      auth: true,
      body: { status },
    });
    loadClaims();
    loadStats();
  } catch (err) {
    alert(err.message);
  }
}

// ---------- Auth modal ----------
const modal = document.getElementById("auth-modal");
function openModal(tab) {
  modal.hidden = false;
  switchTab(tab);
}
document.getElementById("login-btn").addEventListener("click", () => openModal("login"));
document.getElementById("register-btn").addEventListener("click", () => openModal("register"));
document.getElementById("close-modal").addEventListener("click", () => (modal.hidden = true));

function switchTab(tab) {
  document.getElementById("tab-login").classList.toggle("active", tab === "login");
  document.getElementById("tab-register").classList.toggle("active", tab === "register");
  document.getElementById("login-form").hidden = tab !== "login";
  document.getElementById("register-form").hidden = tab !== "register";
}
document.getElementById("tab-login").addEventListener("click", () => switchTab("login"));
document.getElementById("tab-register").addEventListener("click", () => switchTab("register"));

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("login-message");
  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: {
        email: document.getElementById("login-email").value,
        password: document.getElementById("login-password").value,
      },
    });
    setSession(data.token, data.user);
    modal.hidden = true;
    showView("browse");
  } catch (err) {
    msg.textContent = err.message;
  }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("register-message");
  try {
    const data = await api("/auth/register", {
      method: "POST",
      body: {
        name: document.getElementById("reg-name").value,
        email: document.getElementById("reg-email").value,
        password: document.getElementById("reg-password").value,
        role: document.getElementById("reg-role").value,
        org_name: document.getElementById("reg-org").value,
      },
    });
    setSession(data.token, data.user);
    modal.hidden = true;
    showView("browse");
  } catch (err) {
    msg.textContent = err.message;
  }
});

document.getElementById("logout-btn").addEventListener("click", () => {
  clearSession();
  showView("browse");
});

// ---------- Init ----------
renderAuthState();
loadStats();
loadDonations();
