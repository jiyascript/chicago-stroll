const $ = (selector) => document.querySelector(selector);

const state = { threadId: null, lastPrompt: "" };
const sections = ["#loading-state", "#clarification", "#itinerary", "#error-state"];

function show(selector) {
  sections.forEach((item) => $(item).classList.add("hidden"));
  if (selector) {
    $(selector).classList.remove("hidden");
    $(selector).scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

async function requestPlan(endpoint, payload) {
  show("#loading-state");
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`The planner returned ${response.status}.`);
    handleResponse(await response.json());
  } catch (error) {
    $("#error-message").textContent = error.message || "We couldn’t build your day just yet. Please try again.";
    show("#error-state");
  }
}

function handleResponse(data) {
  state.threadId = data.thread_id;
  if (data.itinerary) {
    renderItinerary(data.itinerary);
  } else if (data.clarification_question) {
    $("#clarification-question").textContent = data.clarification_question;
    $("#clarification-answer").value = "";
    show("#clarification");
    setTimeout(() => $("#clarification-answer").focus(), 500);
  } else {
    throw new Error("The planner finished without an itinerary. Try adding a date, time, budget, and interests.");
  }
}

function safeUrl(value) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch { return null; }
}

function renderItinerary(itinerary) {
  $("#itinerary-title").textContent = itinerary.title;
  $("#itinerary-summary").textContent = itinerary.summary;
  const route = $("#route");
  route.replaceChildren();

  itinerary.stops.forEach((stop, index) => {
    const place = stop.place;
    const article = document.createElement("article");
    article.className = "stop";
    const website = safeUrl(place.website);
    article.innerHTML = `
      <div class="stop-time">${escapeHtml(stop.arrival_time)}<small>TO ${escapeHtml(stop.departure_time)}</small></div>
      <div class="stop-line"><span class="stop-dot"></span></div>
      <div class="stop-card">
        <div class="stop-meta">
          <span class="pill accent">Stop ${index + 1}</span>
          <span class="pill">${escapeHtml(place.category.replaceAll("_", " "))}</span>
          <span class="pill">${escapeHtml(place.neighborhood)}</span>
          <span class="pill">${escapeHtml(place.price_tier)}</span>
        </div>
        <h3>${escapeHtml(place.name)}</h3>
        <p class="description">${escapeHtml(place.description)}</p>
        <p class="reason">${escapeHtml(stop.reason)}</p>
        <div class="stop-details">
          <span>◷ ${escapeHtml(String(place.typical_visit_minutes))} min</span>
          ${place.address ? `<span>⌖ ${escapeHtml(place.address)}</span>` : ""}
          ${website ? `<a href="${escapeHtml(website)}" target="_blank" rel="noreferrer">Visit website ↗</a>` : ""}
        </div>
      </div>`;
    route.appendChild(article);
  });
  show("#itinerary");
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);
}

$("#planner-form").addEventListener("submit", (event) => {
  event.preventDefault();
  state.lastPrompt = $("#request").value.trim();
  if (state.lastPrompt) requestPlan("/plan", { message: state.lastPrompt });
});

$("#clarification-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const message = $("#clarification-answer").value.trim();
  if (message && state.threadId) requestPlan("/continue", { thread_id: state.threadId, message });
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    $("#request").value = button.dataset.prompt;
    $("#request").focus();
  });
});

function resetPlanner() {
  state.threadId = null;
  show(null);
  $("#planner").scrollIntoView({ behavior: "smooth" });
  setTimeout(() => $("#request").focus(), 500);
}

$("#start-over").addEventListener("click", resetPlanner);
$("#retry-button").addEventListener("click", resetPlanner);
