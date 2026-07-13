const STORE_KEY = "venturefoundry.pefy-gg.v1";
const REVIEW_KEY = "venturefoundry.pefy-gg.review.v1";
const SEED_URL = "data/pefy-gg-pilot.json";

const WEIGHTS = {
  strategicFit: 0.10,
  problemSeverity: 0.10,
  marketAccess: 0.10,
  valueEvidence: 0.10,
  customerCommitment: 0.15,
  feasibility: 0.10,
  economicViability: 0.15,
  executionCapacity: 0.10,
  trust: 0.05,
  scalability: 0.05
};

const VIEW_META = {
  command: ["Executive portfolio governance", "Command Center", "New portfolio item"],
  portfolio: ["Comparative venture decisions", "Portfolio", "New portfolio item"],
  experiments: ["Evidence before expansion", "Experiments", "New experiment"],
  risks: ["Proportional control", "Risks & Controls", "New risk"],
  decisions: ["Auditable leadership action", "Decision Log", "New decision"],
  review: ["Weekly operating rhythm", "Weekly Review", "Add decision"],
  settings: ["Controlled portability", "Data & Settings", "Export JSON"]
};

const SCHEMAS = {
  portfolio: [
    ["name", "Initiative name", "text", true, "full"],
    ["class", "Portfolio class", "text", true],
    ["gate", "Current gate", "select", true, "", ["G0","G1","G2","G3","G4","G5","G6","G7"]],
    ["owner", "Decision owner", "text", true],
    ["risk", "Residual risk", "select", true, "", ["Low","Moderate","High","Critical"]],
    ["decision", "Current decision", "text", true, "full"],
    ["nextEvidence", "Next required evidence", "textarea", true, "full"],
    ["reviewDate", "Next review date", "date", true],
    ["protected", "Protected priority", "checkbox", false],
    ["confidence", "Evidence confidence (0–1)", "number", true],
    ["strategicFit", "Strategic fit (0–5)", "number", true],
    ["problemSeverity", "Problem severity (0–5)", "number", true],
    ["marketAccess", "Market timing/access (0–5)", "number", true],
    ["valueEvidence", "Value evidence (0–5)", "number", true],
    ["customerCommitment", "Customer commitment (0–5)", "number", true],
    ["feasibility", "Feasibility (0–5)", "number", true],
    ["economicViability", "Economic viability (0–5)", "number", true],
    ["executionCapacity", "Execution capacity (0–5)", "number", true],
    ["trust", "Risk/compliance/trust (0–5)", "number", true],
    ["scalability", "Scalability/defensibility (0–5)", "number", true]
  ],
  experiments: [
    ["title", "Experiment title", "text", true, "full"],
    ["ventureId", "Venture ID", "text", true],
    ["owner", "Experiment owner", "text", true],
    ["status", "Status", "select", true, "", ["planned","running","completed","invalid"]],
    ["dueDate", "Due date", "date", true],
    ["assumption", "Critical assumption", "textarea", true, "full"],
    ["passThreshold", "Pass threshold", "textarea", true, "full"],
    ["decisionOnPass", "Decision on pass", "textarea", true, "full"],
    ["decisionOnFail", "Decision on fail", "textarea", true, "full"]
  ],
  risks: [
    ["description", "Risk description", "textarea", true, "full"],
    ["ventureId", "Venture ID", "text", true],
    ["category", "Category", "text", true],
    ["likelihood", "Likelihood (1–5)", "number", true],
    ["impact", "Impact (1–5)", "number", true],
    ["owner", "Risk owner", "text", true],
    ["status", "Status", "select", true, "", ["open","treating","accepted","closed"]],
    ["control", "Current control / treatment", "textarea", true, "full"]
  ],
  decisions: [
    ["date", "Decision date", "date", true],
    ["scope", "Scope", "text", true],
    ["owner", "Decision owner", "text", true],
    ["status", "Status", "select", true, "", ["proposed","approved","conditional","superseded","closed"]],
    ["decision", "Decision", "textarea", true, "full"],
    ["rationale", "Rationale and evidence basis", "textarea", true, "full"]
  ]
};

let state;
let currentView = "command";
let experimentFilter = "all";
let dialogContext = null;

const byId = id => document.getElementById(id);
const qsa = selector => [...document.querySelectorAll(selector)];
const clone = value => JSON.parse(JSON.stringify(value));
const todayISO = () => new Date().toISOString().slice(0, 10);
const uid = prefix => `${prefix}-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2,6).toUpperCase()}`;

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[char]));
}

function riskModifier(risk) {
  return ({Low: 1, Moderate: .9, High: .75, Critical: 0})[risk] ?? .9;
}

function decisionScore(item) {
  const weighted = Object.entries(WEIGHTS).reduce((sum, [key, weight]) => sum + ((Number(item.scores?.[key]) || 0) * weight), 0) / 5 * 100;
  return Math.round(weighted * (Number(item.confidence) || .5) * (Number(item.riskModifier) || riskModifier(item.risk)));
}

function decisionBand(score) {
  if (score >= 80) return ["Scale / institutionalize", "good"];
  if (score >= 65) return ["Controlled continuation", "good"];
  if (score >= 50) return ["Focused validation", "warn"];
  if (score >= 35) return ["Redesign / return gate", "warn"];
  return ["Stop / archive", "risk"];
}

function riskScore(risk) {
  return (Number(risk.likelihood) || 0) * (Number(risk.impact) || 0);
}

function riskBand(score) {
  if (score >= 21) return ["Stop", "risk"];
  if (score >= 16) return ["Gate hold", "risk"];
  if (score >= 10) return ["Sponsor review", "warn"];
  if (score >= 5) return ["Treat", "warn"];
  return ["Team manage", "good"];
}

function formatDate(value) {
  if (!value) return "Not set";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("en", {day:"2-digit", month:"short", year:"numeric"}).format(date);
}

function isOverdue(value) {
  return Boolean(value && value < todayISO());
}

function saveState(message = "Saved locally") {
  localStorage.setItem(STORE_KEY, JSON.stringify(state));
  byId("saveState").textContent = message;
  byId("storageState").textContent = "Local";
  setTimeout(() => { byId("saveState").textContent = "Saved locally"; }, 1300);
}

function toast(message) {
  const node = byId("toast");
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => node.classList.remove("show"), 2200);
}

async function bootstrap() {
  const stored = localStorage.getItem(STORE_KEY);
  if (stored) {
    try { state = JSON.parse(stored); }
    catch { localStorage.removeItem(STORE_KEY); }
  }
  if (!state) {
    const response = await fetch(SEED_URL, {cache: "no-store"});
    if (!response.ok) throw new Error(`Unable to load pilot dataset (${response.status}).`);
    state = await response.json();
    saveState("Pilot data initialized");
  }
  normalizeState();
  bindEvents();
  renderAll();
  registerServiceWorker();
}

function normalizeState() {
  state.portfolio ||= [];
  state.experiments ||= [];
  state.risks ||= [];
  state.decisions ||= [];
  state.settings ||= {protectedPriorityLimit: 3, gates: ["G0","G1","G2","G3","G4","G5","G6","G7"]};
  state.meta ||= {name: "VentureFoundry Dataset", version: "1.0.0", status: "controlled-pilot"};
  state.portfolio.forEach(item => {
    item.scores ||= {};
    item.riskModifier = riskModifier(item.risk);
  });
}

function bindEvents() {
  qsa(".nav-item").forEach(button => button.addEventListener("click", () => setView(button.dataset.view)));
  byId("primaryAction").addEventListener("click", handlePrimaryAction);
  byId("exportQuick").addEventListener("click", exportJson);
  byId("exportJson").addEventListener("click", exportJson);
  byId("exportPortfolioCsv").addEventListener("click", exportPortfolioCsv);
  byId("importJson").addEventListener("change", importJson);
  byId("resetData").addEventListener("click", resetData);
  byId("portfolioSearch").addEventListener("input", renderPortfolio);
  byId("portfolioClassFilter").addEventListener("change", renderPortfolio);
  byId("portfolioRiskFilter").addEventListener("change", renderPortfolio);
  byId("portfolioGateFilter").addEventListener("change", renderPortfolio);
  qsa("[data-experiment-filter]").forEach(button => button.addEventListener("click", () => {
    experimentFilter = button.dataset.experimentFilter;
    qsa("[data-experiment-filter]").forEach(node => node.classList.toggle("is-active", node === button));
    renderExperiments();
  }));
  byId("copyBrief").addEventListener("click", copyWeeklyBrief);
  byId("reviewChecklist").addEventListener("change", saveReviewChecklist);
  byId("entityForm").addEventListener("submit", handleDialogSubmit);
  document.addEventListener("click", handleDelegatedClick);
}

function setView(view) {
  currentView = view;
  qsa(".nav-item").forEach(button => button.classList.toggle("is-active", button.dataset.view === view));
  qsa("[data-view-panel]").forEach(panel => panel.classList.toggle("is-active", panel.dataset.viewPanel === view));
  const [eyebrow, title, action] = VIEW_META[view];
  byId("viewEyebrow").textContent = eyebrow;
  byId("viewTitle").textContent = title;
  byId("primaryAction").textContent = action;
  byId("main").focus({preventScroll: true});
}

function handlePrimaryAction() {
  if (currentView === "settings") return exportJson();
  const type = currentView === "command" ? "portfolio" : currentView === "review" ? "decisions" : currentView;
  if (!SCHEMAS[type]) return;
  openDialog(type);
}

function renderAll() {
  byId("datasetVersion").textContent = state.meta.version || "1.0";
  populateFilters();
  renderCommandCenter();
  renderPortfolio();
  renderExperiments();
  renderRisks();
  renderDecisions();
  renderWeeklyReview();
  renderSettings();
  restoreReviewChecklist();
}

function populateFilters() {
  const classSelect = byId("portfolioClassFilter");
  const currentClass = classSelect.value;
  classSelect.innerHTML = '<option value="">All classes</option>' + [...new Set(state.portfolio.map(item => item.class))].sort().map(value => `<option>${escapeHtml(value)}</option>`).join("");
  classSelect.value = currentClass;
  const gateSelect = byId("portfolioGateFilter");
  const currentGate = gateSelect.value;
  gateSelect.innerHTML = '<option value="">All gates</option>' + (state.settings.gates || []).map(value => `<option>${escapeHtml(value)}</option>`).join("");
  gateSelect.value = currentGate;
}

function renderCommandCenter() {
  const protectedItems = state.portfolio.filter(item => item.protected);
  const highRisks = state.risks.filter(item => riskScore(item) >= 10 && item.status !== "closed");
  const openExperiments = state.experiments.filter(item => !["completed","invalid"].includes(item.status));
  const avgScore = state.portfolio.length ? Math.round(state.portfolio.reduce((sum, item) => sum + decisionScore(item), 0) / state.portfolio.length) : 0;
  const metrics = [
    ["Portfolio items", state.portfolio.length, "Backbone, engines and strategic options", ""],
    ["Protected priorities", protectedItems.length, `Limit: ${state.settings.protectedPriorityLimit}`, protectedItems.length <= state.settings.protectedPriorityLimit ? "good" : "risk"],
    ["Open experiments", openExperiments.length, `${openExperiments.filter(item => isOverdue(item.dueDate)).length} overdue`, openExperiments.some(item => isOverdue(item.dueDate)) ? "warn" : ""],
    ["Evidence-adjusted readiness", `${avgScore}%`, "Portfolio average; not a success prediction", avgScore >= 65 ? "good" : avgScore >= 50 ? "warn" : "risk"]
  ];
  byId("metricGrid").innerHTML = metrics.map(([label,value,detail,tone]) => `<article class="metric-card"><div class="metric-label">${label}</div><div class="metric-value ${tone}">${value}</div><div class="metric-detail">${detail}</div></article>`).join("");

  const limit = Number(state.settings.protectedPriorityLimit) || 3;
  const indicator = byId("priorityLimitIndicator");
  indicator.textContent = `${protectedItems.length} / ${limit}`;
  indicator.className = `limit-indicator ${protectedItems.length <= limit ? "good" : "risk"}`;
  byId("protectedPriorities").innerHTML = protectedItems.length ? protectedItems.map(item => {
    const score = decisionScore(item);
    return `<div class="stack-item"><div><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.decision)}</small></div><div class="stack-meta"><span class="badge badge-${decisionBand(score)[1]}">${score}%</span><small>${escapeHtml(item.gate)}</small></div></div>`;
  }).join("") : '<div class="empty-state">No protected priority is assigned.</div>';

  const gateCounts = Object.fromEntries((state.settings.gates || []).map(gate => [gate, 0]));
  state.portfolio.forEach(item => gateCounts[item.gate] = (gateCounts[item.gate] || 0) + 1);
  byId("gateDistribution").innerHTML = Object.entries(gateCounts).map(([gate,count]) => `<div class="gate-card"><span>${gate}</span><strong>${count}</strong><span>${count === 1 ? "initiative" : "initiatives"}</span></div>`).join("");

  const attention = [
    ...state.experiments.filter(item => isOverdue(item.dueDate) && item.status !== "completed").map(item => ({title: item.title, detail: `Experiment overdue · ${formatDate(item.dueDate)}`, badge: "Overdue", tone: "risk"})),
    ...highRisks.map(item => ({title: item.description, detail: `${item.owner} · risk score ${riskScore(item)}`, badge: riskBand(riskScore(item))[0], tone: riskBand(riskScore(item))[1]})),
    ...state.portfolio.filter(item => isOverdue(item.reviewDate)).map(item => ({title: item.name, detail: `Portfolio review overdue · ${formatDate(item.reviewDate)}`, badge: "Review", tone: "warn"}))
  ].slice(0, 7);
  byId("attentionList").innerHTML = attention.length ? attention.map(item => `<div class="stack-item"><div><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.detail)}</small></div><span class="badge badge-${item.tone}">${escapeHtml(item.badge)}</span></div>`).join("") : '<div class="empty-state">No overdue or high-exposure item.</div>';

  const flagship = state.portfolio.find(item => item.id === "ELV-001") || state.portfolio.find(item => /EL-VECTOR/i.test(item.name));
  const flagshipExperiments = state.experiments.filter(item => item.ventureId === flagship?.id);
  const completed = flagshipExperiments.filter(item => item.status === "completed").length;
  const riskOpen = state.risks.filter(item => item.ventureId === flagship?.id && item.status !== "closed").length;
  const rows = flagship ? [
    ["Decision score", decisionScore(flagship), `${decisionScore(flagship)}%`],
    ["Experiments", flagshipExperiments.length ? Math.round(completed / flagshipExperiments.length * 100) : 0, `${completed}/${flagshipExperiments.length}`],
    ["Customer commitment", (Number(flagship.scores.customerCommitment) || 0) * 20, `${flagship.scores.customerCommitment}/5`],
    ["Open risk controls", Math.max(0, 100 - riskOpen * 20), String(riskOpen)]
  ] : [];
  byId("flagshipPulse").innerHTML = `<div class="pulse">${rows.map(([label,width,value]) => `<div class="pulse-row"><span class="pulse-label">${label}</span><div class="progress"><span style="width:${Math.min(100,width)}%"></span></div><span class="pulse-value">${value}</span></div>`).join("")}</div>`;
}

function filteredPortfolio() {
  const query = byId("portfolioSearch").value.trim().toLowerCase();
  const classFilter = byId("portfolioClassFilter").value;
  const riskFilter = byId("portfolioRiskFilter").value;
  const gateFilter = byId("portfolioGateFilter").value;
  return state.portfolio.filter(item => {
    const haystack = [item.name,item.class,item.owner,item.decision,item.nextEvidence,item.gate,item.risk].join(" ").toLowerCase();
    return (!query || haystack.includes(query)) && (!classFilter || item.class === classFilter) && (!riskFilter || item.risk === riskFilter) && (!gateFilter || item.gate === gateFilter);
  });
}

function renderPortfolio() {
  const rows = filteredPortfolio();
  byId("portfolioTableBody").innerHTML = rows.length ? rows.map(item => {
    const score = decisionScore(item);
    const [band,tone] = decisionBand(score);
    const overdue = isOverdue(item.reviewDate);
    return `<tr>
      <td><span class="cell-title">${escapeHtml(item.name)}</span><span class="cell-subtitle">${item.protected ? "Protected priority" : "Controlled portfolio item"}</span></td>
      <td><span class="badge badge-info">${escapeHtml(item.gate)}</span><span class="cell-subtitle">${escapeHtml(item.class)}</span></td>
      <td class="score-cell"><span class="score-number">${score}%</span><div class="progress"><span style="width:${score}%"></span></div><span class="cell-subtitle">${escapeHtml(band)}</span></td>
      <td><span class="badge badge-${item.risk === "Low" ? "good" : item.risk === "Moderate" ? "warn" : "risk"}">${escapeHtml(item.risk)}</span></td>
      <td><strong>${escapeHtml(item.decision)}</strong><span class="cell-subtitle">Confidence ${Math.round((Number(item.confidence)||0)*100)}%</span></td>
      <td>${escapeHtml(item.nextEvidence)}<span class="cell-subtitle ${overdue ? "risk" : ""}">${overdue ? "Overdue · " : "Review · "}${formatDate(item.reviewDate)}</span></td>
      <td>${escapeHtml(item.owner)}</td>
      <td><div class="row-actions"><button class="row-button" data-edit-type="portfolio" data-edit-id="${escapeHtml(item.id)}" type="button">Edit</button></div></td>
    </tr>`;
  }).join("") : '<tr><td colspan="8" class="empty-state">No portfolio item matches the filters.</td></tr>';
}

function renderExperiments() {
  const items = state.experiments.filter(item => experimentFilter === "all" || item.status === experimentFilter);
  byId("experimentBoard").innerHTML = items.length ? items.map(item => {
    const overdue = isOverdue(item.dueDate) && !["completed","invalid"].includes(item.status);
    const statusTone = item.status === "completed" ? "good" : item.status === "running" ? "info" : item.status === "invalid" ? "risk" : "warn";
    return `<article class="record-card">
      <header><div><p class="kicker">${escapeHtml(item.id)}</p><h3>${escapeHtml(item.title)}</h3></div><span class="badge badge-${statusTone}">${escapeHtml(item.status)}</span></header>
      <p>${escapeHtml(item.assumption)}</p>
      <dl><dt>Owner</dt><dd>${escapeHtml(item.owner)}</dd><dt>Due</dt><dd>${overdue ? '<span class="badge badge-risk">Overdue</span> ' : ""}${formatDate(item.dueDate)}</dd><dt>Pass</dt><dd>${escapeHtml(item.passThreshold)}</dd><dt>Evidence</dt><dd>${item.evidence?.length || 0} linked item(s)</dd></dl>
      <footer><span class="cell-subtitle">${escapeHtml(item.ventureId)}</span><button class="row-button" data-edit-type="experiments" data-edit-id="${escapeHtml(item.id)}" type="button">Edit experiment</button></footer>
    </article>`;
  }).join("") : '<div class="empty-state">No experiment in this status.</div>';
}

function renderRisks() {
  const rows = [...state.risks].sort((a,b) => riskScore(b) - riskScore(a));
  byId("riskTableBody").innerHTML = rows.length ? rows.map(item => {
    const score = riskScore(item);
    const [band,tone] = riskBand(score);
    return `<tr><td><span class="cell-title">${escapeHtml(item.description)}</span><span class="cell-subtitle">${escapeHtml(item.id)} · ${escapeHtml(item.ventureId)}</span></td><td>${escapeHtml(item.category)}</td><td><span class="score-number">${score}</span><span class="badge badge-${tone}">${band}</span></td><td>${escapeHtml(item.control)}</td><td>${escapeHtml(item.owner)}</td><td><span class="badge badge-${item.status === "closed" ? "good" : "warn"}">${escapeHtml(item.status)}</span></td><td><button class="row-button" data-edit-type="risks" data-edit-id="${escapeHtml(item.id)}" type="button">Edit</button></td></tr>`;
  }).join("") : '<tr><td colspan="7" class="empty-state">No risk record.</td></tr>';
}

function renderDecisions() {
  const rows = [...state.decisions].sort((a,b) => String(b.date).localeCompare(String(a.date)));
  byId("decisionTimeline").innerHTML = rows.length ? rows.map(item => `<article class="timeline-item"><time class="timeline-date">${formatDate(item.date)}</time><span class="timeline-dot" aria-hidden="true"></span><div class="timeline-card"><div class="panel-heading" style="padding:0 0 12px;border:0"><div><p class="kicker">${escapeHtml(item.scope)} · ${escapeHtml(item.id)}</p><h3>${escapeHtml(item.decision)}</h3></div><span class="badge badge-${item.status === "approved" ? "good" : item.status === "proposed" ? "warn" : "info"}">${escapeHtml(item.status)}</span></div><p>${escapeHtml(item.rationale)}</p><p><strong>Owner:</strong> ${escapeHtml(item.owner)} · <button class="row-button" data-edit-type="decisions" data-edit-id="${escapeHtml(item.id)}" type="button">Edit</button></p></div></article>`).join("") : '<div class="empty-state">No decision recorded.</div>';
}

function weeklyBriefHtml() {
  const protectedItems = state.portfolio.filter(item => item.protected);
  const overdueExperiments = state.experiments.filter(item => isOverdue(item.dueDate) && !["completed","invalid"].includes(item.status));
  const topRisks = [...state.risks].filter(item => item.status !== "closed").sort((a,b) => riskScore(b)-riskScore(a)).slice(0,3);
  const comingReviews = [...state.portfolio].sort((a,b) => String(a.reviewDate).localeCompare(String(b.reviewDate))).slice(0,4);
  return `
    <h3>Executive status</h3>
    <p>${protectedItems.length} protected priorities are active against a limit of ${state.settings.protectedPriorityLimit}. ${protectedItems.length <= state.settings.protectedPriorityLimit ? "Portfolio concentration remains within policy." : "The priority limit is exceeded and requires immediate de-prioritization."}</p>
    <h3>Protected priorities</h3><ul>${protectedItems.map(item => `<li><strong>${escapeHtml(item.name)}</strong> — ${escapeHtml(item.decision)}; decision score ${decisionScore(item)}%; next evidence: ${escapeHtml(item.nextEvidence)}.</li>`).join("") || "<li>None assigned.</li>"}</ul>
    <h3>Experiments requiring attention</h3><ul>${overdueExperiments.map(item => `<li><strong>${escapeHtml(item.title)}</strong> was due ${formatDate(item.dueDate)}; owner: ${escapeHtml(item.owner)}.</li>`).join("") || "<li>No overdue experiment.</li>"}</ul>
    <h3>Top residual risks</h3><ul>${topRisks.map(item => `<li><strong>${riskScore(item)} — ${escapeHtml(item.description)}</strong> Control: ${escapeHtml(item.control)} Owner: ${escapeHtml(item.owner)}.</li>`).join("") || "<li>No open risk.</li>"}</ul>
    <h3>Next reviews</h3><ul>${comingReviews.map(item => `<li>${escapeHtml(item.name)} — ${formatDate(item.reviewDate)} (${escapeHtml(item.gate)}).</li>`).join("")}</ul>
    <h3>Required leadership decisions</h3><p>Confirm no more than three next priorities, approve owners and due dates, stop or defer unsupported work, and record any continue, change, stop or scale decision.</p>`;
}

function renderWeeklyReview() {
  byId("weeklyBrief").innerHTML = weeklyBriefHtml();
}

function renderSettings() {
  const protectedCount = state.portfolio.filter(item => item.protected).length;
  byId("governanceStatus").innerHTML = [
    ["Dataset", state.meta.name],
    ["Version", state.meta.version],
    ["Status", state.meta.status],
    ["Confidentiality", state.meta.confidentiality || "Not classified"],
    ["Protected priorities", `${protectedCount}/${state.settings.protectedPriorityLimit}`],
    ["Portfolio records", state.portfolio.length],
    ["Experiment records", state.experiments.length],
    ["Risk records", state.risks.length],
    ["Decision records", state.decisions.length],
    ["Last local save", new Date().toLocaleString()]
  ].map(([term,value]) => `<dt>${escapeHtml(term)}</dt><dd>${escapeHtml(value)}</dd>`).join("");
}

function handleDelegatedClick(event) {
  const edit = event.target.closest("[data-edit-type]");
  if (!edit) return;
  openDialog(edit.dataset.editType, edit.dataset.editId);
}

function openDialog(type, id = null) {
  const collection = state[type];
  const record = id ? collection.find(item => item.id === id) : null;
  dialogContext = {type, id};
  byId("dialogKicker").textContent = record ? `Edit ${type.replace(/s$/, "")}` : `New ${type.replace(/s$/, "")}`;
  byId("dialogTitle").textContent = record?.name || record?.title || record?.description || record?.decision || "Create record";
  byId("dialogFields").innerHTML = SCHEMAS[type].map(field => fieldHtml(field, record, type)).join("");
  byId("entityDialog").showModal();
}

function fieldHtml([key,label,type,required,layout,options], record, collectionType) {
  let value;
  if (collectionType === "portfolio" && key in WEIGHTS) value = record?.scores?.[key] ?? 0;
  else value = record?.[key] ?? (type === "date" ? todayISO() : type === "checkbox" ? false : type === "number" ? 0 : "");
  const common = `name="${key}" id="field-${key}" ${required ? "required" : ""}`;
  let control;
  if (type === "textarea") control = `<textarea ${common}>${escapeHtml(value)}</textarea>`;
  else if (type === "select") control = `<select ${common}>${options.map(option => `<option ${option === value ? "selected" : ""}>${escapeHtml(option)}</option>`).join("")}</select>`;
  else if (type === "checkbox") control = `<input ${common} type="checkbox" ${value ? "checked" : ""}>`;
  else {
    const attrs = type === "number" ? (key === "confidence" ? 'min="0" max="1" step="0.05"' : 'min="0" max="5" step="1"') : "";
    control = `<input ${common} type="${type}" value="${escapeHtml(value)}" ${attrs}>`;
  }
  return `<div class="dialog-field ${layout || ""}"><label for="field-${key}">${escapeHtml(label)}</label>${control}</div>`;
}

function handleDialogSubmit(event) {
  if (event.submitter?.value === "cancel") { dialogContext = null; return; }
  event.preventDefault();
  const {type,id} = dialogContext;
  const form = new FormData(event.currentTarget);
  const collection = state[type];
  const existingIndex = id ? collection.findIndex(item => item.id === id) : -1;
  const record = existingIndex >= 0 ? clone(collection[existingIndex]) : {id: uid(type === "portfolio" ? "VNT" : type === "experiments" ? "EXP" : type === "risks" ? "RSK" : "DEC")};
  SCHEMAS[type].forEach(([key,,, , ,]) => {
    const field = byId(`field-${key}`);
    let value = field?.type === "checkbox" ? field.checked : form.get(key);
    if (field?.type === "number") value = Number(value);
    if (type === "portfolio" && key in WEIGHTS) {
      record.scores ||= {};
      record.scores[key] = Math.max(0, Math.min(5, Number(value) || 0));
    } else record[key] = value;
  });
  if (type === "portfolio") record.riskModifier = riskModifier(record.risk);
  if (type === "experiments") record.evidence ||= [];
  if (existingIndex >= 0) collection[existingIndex] = record; else collection.unshift(record);
  saveState();
  byId("entityDialog").close();
  dialogContext = null;
  renderAll();
  toast(existingIndex >= 0 ? "Record updated" : "Record created");
}

function download(filename, contents, type) {
  const blob = new Blob([contents], {type});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function exportJson() {
  state.meta.updated = todayISO();
  saveState();
  download(`venturefoundry-pefy-gg-${todayISO()}.json`, JSON.stringify(state, null, 2), "application/json;charset=utf-8");
  toast("Complete dataset exported");
}

function exportPortfolioCsv() {
  const headers = ["ID","Initiative","Class","Gate","Owner","Protected","Residual Risk","Decision Score","Decision","Next Evidence","Review Date"];
  const rows = state.portfolio.map(item => [item.id,item.name,item.class,item.gate,item.owner,item.protected,item.risk,decisionScore(item),item.decision,item.nextEvidence,item.reviewDate]);
  const csv = [headers, ...rows].map(row => row.map(value => `"${String(value ?? "").replaceAll('"','""')}"`).join(",")).join("\n");
  download(`pefy-gg-portfolio-${todayISO()}.csv`, csv, "text/csv;charset=utf-8");
  toast("Portfolio CSV exported");
}

async function importJson(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  try {
    const imported = JSON.parse(await file.text());
    validateImport(imported);
    state = imported;
    normalizeState();
    saveState("Imported dataset saved");
    renderAll();
    toast("Dataset imported successfully");
  } catch (error) {
    toast(`Import failed: ${error.message}`);
  } finally {
    event.target.value = "";
  }
}

function validateImport(data) {
  if (!data || typeof data !== "object") throw new Error("Root JSON object is required.");
  for (const key of ["portfolio","experiments","risks","decisions"]) if (!Array.isArray(data[key])) throw new Error(`Missing array: ${key}.`);
  if (!data.meta || !data.settings) throw new Error("Missing meta or settings object.");
}

async function resetData() {
  if (!confirm("Reset all browser changes and restore the PEFY-GG pilot dataset?")) return;
  const response = await fetch(`${SEED_URL}?reset=${Date.now()}`, {cache:"no-store"});
  if (!response.ok) return toast("Reset failed: seed dataset is unavailable");
  state = await response.json();
  normalizeState();
  localStorage.removeItem(REVIEW_KEY);
  saveState("Pilot dataset restored");
  renderAll();
  toast("Pilot dataset restored");
}

function saveReviewChecklist() {
  const values = Object.fromEntries(qsa("[data-review-check]").map(input => [input.dataset.reviewCheck, input.checked]));
  localStorage.setItem(REVIEW_KEY, JSON.stringify(values));
  updateReviewCompletion();
}

function restoreReviewChecklist() {
  let values = {};
  try { values = JSON.parse(localStorage.getItem(REVIEW_KEY) || "{}"); } catch {}
  qsa("[data-review-check]").forEach(input => input.checked = Boolean(values[input.dataset.reviewCheck]));
  updateReviewCompletion();
}

function updateReviewCompletion() {
  const boxes = qsa("[data-review-check]");
  const percentage = boxes.length ? Math.round(boxes.filter(input => input.checked).length / boxes.length * 100) : 0;
  byId("reviewCompletion").textContent = `${percentage}%`;
  byId("reviewProgress").style.width = `${percentage}%`;
}

async function copyWeeklyBrief() {
  const text = byId("weeklyBrief").innerText;
  try { await navigator.clipboard.writeText(text); toast("Weekly brief copied"); }
  catch { toast("Clipboard access is unavailable"); }
}

function registerServiceWorker() {
  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
    navigator.serviceWorker.register("service-worker.js").catch(() => {});
  }
}

bootstrap().catch(error => {
  document.body.innerHTML = `<main style="padding:30px;color:white;font-family:system-ui"><h1>VentureFoundry could not start</h1><p>${escapeHtml(error.message)}</p><p>Serve this directory through a local or web HTTP server so the pilot dataset can load.</p></main>`;
});
