/**
 * EmergencyHealth.ai
 * Healthcare Orchestration System
 * Matching exact application screenshots: Symptom Intake, Triage Results,
 * Provider Discovery, Supervisor Dashboard, Google Maps Radar, and 108 Calling
 */

// Application State
let appState = {
    currentView: 'home',
    currentUser: null,
    selectedSymptoms: ['Fever', 'Headache', 'Fatigue'],
    selectedSeverity: 'Moderate',
    userLat: 28.6139,
    userLng: 77.2090,
    hospitalLat: 28.6259,
    hospitalLng: 77.2170,
    ambulanceLat: 28.6189,
    ambulanceLng: 77.2030,
    map: null,
    currentTileLayer: null,
    userMarker: null,
    hospitalMarker: null,
    ambulanceMarker: null,
    routePolyline: null,
    ambulanceSimInterval: null,
    ambulanceSimRunning: false,
    sirenPlaying: false,
    sirenInterval: null,
    audioCtx: null,
    call108Interval: null,
    call108Seconds: 0,
    speechRecognition: null
};

// Map Tiles (Google Maps + OSM)
const MAP_LAYERS = {
    google: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    satellite: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    osm: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
};

// Supervisor Queue Data (Exact Screenshot 5)
const SUPERVISOR_CASES = [
    {
        name: "Rajesh Kumar",
        age: 45,
        severity: "9/10",
        severityLevel: "critical",
        confidence: "92%",
        symptoms: "Chest pain, shortness of breath, sweating",
        vitals: "HR 114 bpm, BP 162/102, SpO2 93%",
        time: "2 minutes ago",
        aiReasoning: "High AI confidence (92%) indicates reliable assessment. High severity score warrants immediate attention. Emergency classification aligns with severe presentation. Elevated vital signs support urgency. Immediate catheterization lab recommendation.",
        riskFactors: ["Acute myocardial ischemia risk", "Tachycardia", "Hypertensive crisis"],
        recommendedAction: "Dispatch ALS Ambulance & Reserve ICU Bed"
    },
    {
        name: "Priya Singh",
        age: 32,
        severity: "7/10",
        severityLevel: "warning",
        confidence: "65%",
        symptoms: "High fever, cough, body ache, dizziness",
        vitals: "HR 98 bpm, Temp 102.4°F, BP 115/78",
        time: "5 minutes ago",
        aiReasoning: "Flagged for Review: Low confidence (<70%) due to conflicting symptom presentation. Requires physician differential diagnosis between severe viral influenza vs Dengue fever.",
        riskFactors: ["High persistent fever (>102°F)", "Borderline thrombocytopenia concern"],
        recommendedAction: "In-Person Clinical Triage & Complete Blood Count (CBC)"
    },
    {
        name: "Amit Patel",
        age: 28,
        severity: "3/10",
        severityLevel: "routine",
        confidence: "78%",
        symptoms: "Mild headache, fatigue, nausea",
        vitals: "HR 74 bpm, Temp 98.6°F, BP 120/80",
        time: "10 minutes ago",
        aiReasoning: "Routine low-severity presentation. Normal vital signs. Auto-approval eligible with tele-consultation support.",
        riskFactors: ["None detected"],
        recommendedAction: "Outpatient Telemedicine Consultation"
    },
    {
        name: "Sunita Reddy",
        age: 55,
        severity: "8/10",
        severityLevel: "warning",
        confidence: "68%",
        symptoms: "Severe abdominal pain, vomiting, fever",
        vitals: "HR 102 bpm, Temp 101.2°F, BP 138/88",
        time: "8 minutes ago",
        aiReasoning: "Flagged for Review: Symptoms could indicate acute appendicitis, cholecystitis, or gastroenteritis. Surgical evaluation advised.",
        riskFactors: ["Acute localized abdomen", "Pyrexia"],
        recommendedAction: "Hospital Emergency Surgical Ward"
    }
];

// Pharmacology & Disease Knowledge Base
const MEDICAL_KNOWLEDGE = {
    paracetamol: {
        names: ["paracetamol", "acetaminophen", "crocin", "calpol", "tylenol", "dolo", "dolo 650"],
        title: "Paracetamol (Acetaminophen)",
        details: "Standard Adult Dose: 500mg-650mg every 4-6 hours (Max 4000mg/24h). Used for fever and mild pain. Avoid in severe liver disease."
    },
    metformin: {
        names: ["metformin", "glycomet"],
        title: "Metformin Hydrochloride",
        details: "Antidiabetic agent for Type-2 Diabetes. Safe with Aspirin under physician guidance. Take with meals to reduce GI upset."
    },
    aspirin: {
        names: ["aspirin", "ecosprin", "disprin"],
        title: "Aspirin (Acetylsalicylic Acid)",
        details: "In suspected cardiac emergencies, 325mg chewable aspirin is recommended. STRICTLY AVOID in suspected Dengue fever due to hemorrhage risk."
    },
    dengue: {
        names: ["dengue", "dengue fever"],
        title: "Dengue Fever Clinical Protocol",
        details: "High fever with severe joint pain. Drink plenty of fluids (ORS, coconut water). Use ONLY Paracetamol for fever; NEVER take Aspirin or Ibuprofen."
    },
    hypertension: {
        names: ["hypertension", "high blood pressure", "high bp"],
        title: "Hypertension Guidelines",
        details: "Target BP < 130/80 mmHg. Avoid over-the-counter decongestants (Pseudoephedrine) and NSAIDs which elevate blood pressure."
    }
};

// Document Load
document.addEventListener('DOMContentLoaded', () => {
    initSpeech();
    setTimeout(() => initMap(), 300);
});

// View Navigation Switcher
function switchMainView(viewId) {
    appState.currentView = viewId;
    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    const sec = document.getElementById(`view-${viewId}`);
    const nav = document.getElementById(`nav-${viewId}`);
    if (sec) sec.classList.add('active');
    if (nav) nav.classList.add('active');

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (viewId === 'radar' && appState.map) {
        setTimeout(() => appState.map.invalidateSize(), 200);
    }
    if (viewId === 'supervisor') {
        selectSupervisorCase(0);
    }
}

// SYMPTOM INTAKE FUNCTIONS (Screenshot 2)
function toggleSymptomPill(el, name) {
    if (el.classList.contains('selected')) {
        el.classList.remove('selected');
        appState.selectedSymptoms = appState.selectedSymptoms.filter(s => s !== name);
    } else {
        el.classList.add('selected');
        if (!appState.selectedSymptoms.includes(name)) {
            appState.selectedSymptoms.push(name);
        }
    }
}

function addCustomSymptomPill() {
    const input = document.getElementById('customSymptomInput');
    const val = input.value.trim();
    if (!val) return;

    appState.selectedSymptoms.push(val);
    const container = document.getElementById('commonSymptomsPills');
    const pill = document.createElement('span');
    pill.className = 'symptom-pill selected';
    pill.innerText = val;
    pill.onclick = () => toggleSymptomPill(pill, val);
    container.appendChild(pill);
    input.value = '';
}

function selectSeverity(level, el) {
    appState.selectedSeverity = level;
    document.querySelectorAll('.severity-choice').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
}

// Execute Assessment & Transition to Triage Results (Screenshot 3)
function executeSymptomAssessment() {
    const isCritical = appState.selectedSeverity === 'Critical' || 
                       appState.selectedSymptoms.some(s => s.toLowerCase().includes('chest') || s.toLowerCase().includes('breath'));

    // Populate Reported Symptoms
    const tagsBox = document.getElementById('reportedSymptomsContainer');
    tagsBox.innerHTML = appState.selectedSymptoms.map(s => `
        <span class="match-pill" style="background: #f1f5f9; color: #0d9488; border-color: #ccfbf1;">${s}</span>
    `).join('');

    const scoreVal = document.getElementById('triageScoreVal');
    const progressBar = document.getElementById('triageProgressBar');
    const priorityBox = document.getElementById('triagePriorityBox');
    const priorityTitle = document.getElementById('triagePriorityTitle');
    const actionText = document.getElementById('triageActionText');
    const catTag = document.getElementById('triageCategoryTag');

    if (isCritical) {
        scoreVal.innerText = "94%";
        progressBar.style.width = "94%";
        catTag.innerText = "🚨 High Urgency (Emergency)";
        priorityBox.className = "priority-banner priority-emergency";
        priorityTitle.innerText = "🚨 High Priority Emergency";
        actionText.innerText = "Immediate trauma center evaluation & ambulance dispatch recommended.";
        speakText("High priority emergency assessment detected. Recommended action: immediate care.");
    } else {
        scoreVal.innerText = "87%";
        progressBar.style.width = "87%";
        catTag.innerText = "Moderate Urgency";
        priorityBox.className = "priority-banner priority-moderate";
        priorityTitle.innerText = "⚠️ Moderate Priority";
        actionText.innerText = "Recommended action: physician consultation within 24 hours.";
    }

    switchMainView('triage');
}

// SUPERVISOR DASHBOARD CASE INSPECTION (Screenshot 5)
function selectSupervisorCase(idx) {
    const c = SUPERVISOR_CASES[idx];
    if (!c) return;

    const pane = document.getElementById('supervisorDetailPane');
    pane.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <h3 style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">${c.name}</h3>
                <div style="font-size: 0.85rem; color: var(--text-muted);">${c.age} years old • ${c.time}</div>
            </div>
            <div style="text-align: right;">
                <span class="match-pill" style="background: #eff6ff; color: #1d4ed8;">AI Score: ${c.confidence}</span>
                <div style="font-size: 1.2rem; font-weight: 900; color: ${c.severityLevel === 'critical' ? '#ef4444' : '#f59e0b'}; margin-top: 0.2rem;">${c.severity}</div>
            </div>
        </div>

        <div style="background: white; border: 1px solid var(--border); border-radius: 8px; padding: 0.85rem; margin-bottom: 0.85rem;">
            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Symptoms & Vitals</div>
            <div style="font-size: 0.9rem; font-weight: 600; color: #0f172a; margin-top: 0.2rem;">${c.symptoms}</div>
            <div style="font-size: 0.85rem; color: #2563eb; margin-top: 0.25rem;">🩺 ${c.vitals}</div>
        </div>

        <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.85rem;">
            <div style="font-size: 0.75rem; color: #7e22ce; text-transform: uppercase; font-weight: 700;">🤖 6-Level AI Clinical Reasoning</div>
            <div style="font-size: 0.85rem; color: #581c87; line-height: 1.5; margin-top: 0.25rem;">
                ${c.aiReasoning}
            </div>
        </div>

        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 0.85rem; margin-bottom: 1.25rem;">
            <div style="font-size: 0.75rem; color: #166534; text-transform: uppercase; font-weight: 700;">Recommended Action</div>
            <div style="font-size: 0.9rem; font-weight: 700; color: #14532d; margin-top: 0.2rem;">${c.recommendedAction}</div>
        </div>

        <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-primary" style="flex: 1;" onclick="alert('Decision Approved for ${c.name} by Dr. Sharma. Care pathway activated.')">
                ✓ Approve Decision
            </button>
            <button class="btn btn-danger" onclick="alert('Case ${c.name} Escalated directly to In-Person Emergency Department!')">
                🚨 Escalate to ER
            </button>
        </div>
    `;
}

// SEMANTIC PROVIDER SEARCH (Screenshot 4)
function runSemanticProviderSearch() {
    const q = document.getElementById('providerSearchInput').value.toLowerCase();
    const spec = document.getElementById('provSpecialtyFilter').value;

    const list = document.getElementById('providerResultsList');
    list.innerHTML = `
        <div class="facility-item">
            <div class="facility-top">
                <div style="display: flex; gap: 0.85rem; align-items: center;">
                    <div style="width: 44px; height: 44px; border-radius: 50%; background: #0d9488; color: white; display: flex; align-items: center; justify-content: center; font-weight: 800;">
                        DSJ
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 1.05rem;">Dr. Sarah Johnson</div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">${spec === 'All' ? 'General Practitioner' : spec} • 15 years exp • English, Hindi</div>
                    </div>
                </div>
                <div>
                    <span class="match-pill">95% Match</span>
                    <span style="font-size: 0.75rem; color: #059669; font-weight: 600; margin-left: 0.35rem;">Accepting New</span>
                </div>
            </div>
            <div class="ai-insight-box">
                <strong>AI Insight:</strong> Best match for "${q || 'reported symptoms'}" with immediate consultation availability.
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                ⭐ 4.8 (234 reviews) • 📍 2.3 km • Available Today • Next available: <strong>2:30 PM</strong>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-primary btn-sm" onclick="alert('Booked with Dr. Sarah Johnson!')">Book Appointment</button>
                <button class="btn btn-secondary btn-sm" onclick="alert('Profile details...')">View Profile</button>
                <a href="tel:108" class="btn btn-secondary btn-sm">📞 Call</a>
            </div>
        </div>
    `;
}

// QUICK LOGIN MODAL FOR JUDGES (Screenshot 1)
function openJudgeLoginModal() {
    document.getElementById('judgeLoginModal').classList.add('active');
}

function closeJudgeLoginModal() {
    document.getElementById('judgeLoginModal').classList.remove('active');
}

function performJudgeLogin(roleName, email) {
    appState.currentUser = { role: roleName, email: email };
    closeJudgeLoginModal();
    alert(`Signed in as ${roleName} (${email}). Demo environment activated!`);
    if (roleName.includes('Supervisor')) {
        switchMainView('supervisor');
    } else {
        switchMainView('intake');
    }
}

// LEAFLET & GOOGLE MAPS TRAUMA RADAR
function initMap() {
    try {
        if (appState.map) return;
        appState.map = L.map('map').setView([appState.userLat, appState.userLng], 14);

        switchMapLayer('google');

        const userIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        const hospitalIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        const ambulanceIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        appState.userMarker = L.marker([appState.userLat, appState.userLng], { icon: userIcon })
            .addTo(appState.map)
            .bindPopup("<b>🚨 EMERGENCY GPS BEACON</b><br>User live location locked.")
            .openPopup();

        appState.hospitalMarker = L.marker([appState.hospitalLat, appState.hospitalLng], { icon: hospitalIcon })
            .addTo(appState.map)
            .bindPopup("<b>🏥 Apex Trauma Center</b><br>🟢 4 ICU Beds Vacant • 24/7 OT Ready<br><a href='javascript:void(0)' onclick='openGoogleMapsNavigation()'>Navigate via Google Maps &rarr;</a>");

        appState.ambulanceMarker = L.marker([appState.ambulanceLat, appState.ambulanceLng], { icon: ambulanceIcon })
            .addTo(appState.map)
            .bindPopup("<b>🚑 ALS Ambulance Unit #12</b><br>En-route with Ventilator & Paramedic.");

        drawEmergencyRoute();
        locateUserPosition();
    } catch (e) {
        console.warn("Map notice:", e);
    }
}

function switchMapLayer(layerKey) {
    if (!appState.map) return;
    if (appState.currentTileLayer) appState.map.removeLayer(appState.currentTileLayer);

    const tileUrl = MAP_LAYERS[layerKey] || MAP_LAYERS.google;
    appState.currentTileLayer = L.tileLayer(tileUrl, {
        attribution: '© Google Maps & OpenStreetMap',
        maxZoom: 20
    }).addTo(appState.map);

    document.querySelectorAll('.map-layer-btn').forEach(b => b.classList.remove('active'));
    if (layerKey === 'google') document.getElementById('btnLayerGoogle')?.classList.add('active');
    else if (layerKey === 'satellite') document.getElementById('btnLayerSatellite')?.classList.add('active');
    else if (layerKey === 'osm') document.getElementById('btnLayerOSM')?.classList.add('active');
}

function drawEmergencyRoute() {
    if (!appState.map) return;
    if (appState.routePolyline) appState.map.removeLayer(appState.routePolyline);

    const latlngs = [
        [appState.ambulanceLat, appState.ambulanceLng],
        [appState.userLat, appState.userLng],
        [appState.hospitalLat, appState.hospitalLng]
    ];

    appState.routePolyline = L.polyline(latlngs, {
        color: '#ef4444',
        weight: 4,
        opacity: 0.8,
        dashArray: '8, 8'
    }).addTo(appState.map);
}

function openGoogleMapsNavigation() {
    locateUserPosition();
    const gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${appState.userLat},${appState.userLng}&destination=${appState.hospitalLat},${appState.hospitalLng}&travelmode=driving`;
    window.open(gmapsUrl, '_blank');
}

function toggleAmbulanceSimulation() {
    const btn = document.getElementById('btnAmbulanceSim');
    if (appState.ambulanceSimRunning) {
        clearInterval(appState.ambulanceSimInterval);
        appState.ambulanceSimRunning = false;
        btn.innerText = "🚑 Simulate Moving Ambulance En-Route";
    } else {
        appState.ambulanceSimRunning = true;
        btn.innerText = "⏹ Stop Ambulance Radar";

        let steps = 0;
        const totalSteps = 60;
        const startLat = appState.ambulanceLat;
        const startLng = appState.ambulanceLng;

        appState.ambulanceSimInterval = setInterval(() => {
            steps++;
            const progress = steps / totalSteps;
            const curLat = startLat + (appState.userLat - startLat) * progress;
            const curLng = startLng + (appState.userLng - startLng) * progress;

            if (appState.ambulanceMarker) appState.ambulanceMarker.setLatLng([curLat, curLng]);
            drawEmergencyRoute();

            const dist = Math.max(0.1, (1.4 * (1 - progress))).toFixed(2);
            const remainingSec = Math.max(0, Math.floor(250 * (1 - progress)));
            const m = Math.floor(remainingSec / 60);
            const s = remainingSec % 60;

            document.getElementById('hudDistanceVal').innerText = `${dist} km`;
            document.getElementById('hudEtaVal').innerText = `${m} min ${s < 10 ? '0' : ''}${s} sec`;

            if (steps >= totalSteps) {
                clearInterval(appState.ambulanceSimInterval);
                appState.ambulanceSimRunning = false;
                btn.innerText = "🚑 Ambulance Arrived On-Scene!";
                document.getElementById('hudEtaVal').innerText = "ARRIVED ON SCENE";
                document.getElementById('hudDistanceVal').innerText = "0.0 km";
                speakText("ALS Ambulance Unit 12 has arrived at patient location.");
            }
        }, 800);
    }
}

// 108 CALLING
function initiate108EmergencyCall() {
    locateUserPosition();
    const modal = document.getElementById('call108Modal');
    modal.classList.add('active');

    appState.call108Seconds = 0;
    const timerEl = document.getElementById('callDurationTimer');
    const transcriptEl = document.getElementById('callTranscriptBox');

    timerEl.innerText = "Connecting to 108...";

    setTimeout(() => {
        timerEl.innerText = "00:01 (Call Active)";
        const script = `National Emergency Ambulance 108. Your live GPS coordinates at ${appState.userLat.toFixed(4)}, ${appState.userLng.toFixed(4)} have been registered. ALS Ambulance Unit 12 is en route with oxygen support. Stay calm, help is arriving.`;
        transcriptEl.innerHTML = `<strong>Dispatcher (108):</strong> "${script}"`;
        speakText(script);

        appState.call108Interval = setInterval(() => {
            appState.call108Seconds++;
            const m = Math.floor(appState.call108Seconds / 60);
            const s = appState.call108Seconds % 60;
            timerEl.innerText = `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s} (Live Dispatch)`;
        }, 1000);
    }, 1500);

    if (/Mobi|Android/i.test(navigator.userAgent)) {
        window.location.href = "tel:108";
    }
}

function close108EmergencyCall() {
    document.getElementById('call108Modal').classList.remove('active');
    clearInterval(appState.call108Interval);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
}

function locateUserPosition() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                appState.userLat = pos.coords.latitude;
                appState.userLng = pos.coords.longitude;
                if (appState.map && appState.userMarker) {
                    appState.map.setView([appState.userLat, appState.userLng], 14);
                    appState.userMarker.setLatLng([appState.userLat, appState.userLng]);
                }
                drawEmergencyRoute();
            },
            () => {},
            { enableHighAccuracy: true, timeout: 8000 }
        );
    }
}

function toggleEmergencySiren() {
    const btn = document.getElementById('btnSirenToggle');
    if (appState.sirenPlaying) {
        appState.sirenPlaying = false;
        clearInterval(appState.sirenInterval);
        btn.innerText = "🚨 Siren: OFF";
    } else {
        appState.sirenPlaying = true;
        btn.innerText = "🚨 Siren: SOUNDING";
        // Web Audio Siren
        if (!appState.audioCtx) appState.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        let high = true;
        appState.sirenInterval = setInterval(() => {
            try {
                const ctx = appState.audioCtx;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(high ? 950 : 650, ctx.currentTime);
                gain.gain.setValueAtTime(0.18, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.35);
                high = !high;
            } catch (e) {}
        }, 400);
    }
}

// AI CHATBOT FOR MEDICINES
function handleChatSend() {
    const input = document.getElementById('chatInput');
    const query = input.value.trim();
    if (!query) return;

    appendChatMessage(query, 'user');
    input.value = '';

    setTimeout(() => {
        let reply = `I have analyzed "${query}" across our clinical database: For persistent symptoms, timely medical triage prevents complications. Monitor vitals and hydration.`;
        const q = query.toLowerCase();

        for (const k in MEDICAL_KNOWLEDGE) {
            const item = MEDICAL_KNOWLEDGE[k];
            if (item.names.some(n => q.includes(n))) {
                reply = `<strong>💊 ${item.title}</strong><br>${item.details}`;
                break;
            }
        }
        appendChatMessage(reply, 'bot');
    }, 400);
}

function sendQuickChat(text) {
    document.getElementById('chatInput').value = text;
    handleChatSend();
}

function appendChatMessage(html, sender) {
    const container = document.getElementById('chatMessages');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.innerHTML = html;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function toggleVoiceForChat() {
    if (!appState.speechRecognition) {
        alert("Voice recognition not supported in this browser. Please use Chrome or Edge.");
        return;
    }
    appState.speechRecognition.onresult = (e) => {
        document.getElementById('chatInput').value = e.results[0][0].transcript;
        handleChatSend();
    };
    appState.speechRecognition.start();
}

function initSpeech() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        appState.speechRecognition = new SpeechRecognition();
        appState.speechRecognition.continuous = false;
        appState.speechRecognition.lang = 'en-IN';
    }
}

function toggleVoiceRecognition() {
    if (!appState.speechRecognition) {
        alert("Voice recognition not supported in this browser.");
        return;
    }
    appState.speechRecognition.onresult = (e) => {
        document.getElementById('customSymptomInput').value = e.results[0][0].transcript;
        addCustomSymptomPill();
    };
    appState.speechRecognition.start();
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.rate = 1.0;
        window.speechSynthesis.speak(u);
    }
}
