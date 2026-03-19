/* =============================================
   🌱 KISHAN SATHI – SCRIPT.JS
   SPA Navigation | AI Simulation | Interactions
   ============================================= */

// ══════════════════════════════════════════
// 📦 STATE
// ══════════════════════════════════════════
const API = "http://127.0.0.1:8000";
const state = {
  currentSection: 'home',
  isDark: false,
  isLoggedIn: false,
  uploadedFile: null,
  chatOpen: false,
  selectedCrop: 'Auto Detect',
  notifOpen: false,
  historyData: [
    { id: 1, crop: '🌾', name: 'Wheat', disease: 'Leaf Rust', status: 'disease', conf: 94, date: '2024-03-18', type: 'wheat' },
    { id: 2, crop: '🌽', name: 'Maize', disease: 'Healthy', status: 'healthy', conf: 99, date: '2024-03-17', type: 'maize' },
    { id: 3, crop: '🍅', name: 'Tomato', disease: 'Late Blight', status: 'disease', conf: 87, date: '2024-03-15', type: 'tomato' },
    { id: 4, crop: '🥔', name: 'Potato', disease: 'Healthy', status: 'healthy', conf: 96, date: '2024-03-14', type: 'potato' },
    { id: 5, crop: '🍚', name: 'Rice', disease: 'Rice Blast', status: 'disease', conf: 91, date: '2024-03-12', type: 'rice' },
    { id: 6, crop: '🌾', name: 'Wheat', disease: 'Powdery Mildew', status: 'disease', conf: 83, date: '2024-03-10', type: 'wheat' },
    { id: 7, crop: '🌱', name: 'Cotton', disease: 'Healthy', status: 'healthy', conf: 97, date: '2024-03-08', type: 'other' },
    { id: 8, crop: '🌽', name: 'Maize', disease: 'Gray Leaf Spot', status: 'disease', conf: 89, date: '2024-03-06', type: 'maize' },
  ]
};

// ══════════════════════════════════════════
// 🧭 SECTION NAVIGATION
// ══════════════════════════════════════════
function showSection(sectionId) {
  // Hide all sections
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

  // Show target section
  const target = document.getElementById(`section-${sectionId}`);
  if (target) {
    target.classList.add('active');
    target.scrollIntoView({ behavior: 'instant', block: 'start' });
    window.scrollTo(0, 0);
  }

  // Update nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.dataset.section === sectionId);
  });

  // Track current
  state.currentSection = sectionId;

  // Close mobile menu
  document.getElementById('navLinks').classList.remove('open');

  // Trigger section-specific init
  if (sectionId === 'dashboard') initDashboardAnimations();
  if (sectionId === 'history') renderHistory();
  if (sectionId === 'result' && !state.uploadedFile) showSection('upload');

  // Close notification dropdown
  closeNotifications();
}

// ══════════════════════════════════════════
// 🌙 DARK MODE TOGGLE
// ══════════════════════════════════════════
function toggleTheme() {
  state.isDark = !state.isDark;
  document.documentElement.setAttribute('data-theme', state.isDark ? 'dark' : 'light');

  // Sync toggles
  const dmToggle = document.getElementById('darkModeToggle');
  if (dmToggle) dmToggle.checked = state.isDark;

  // Swap icons
  const sunIcon = document.querySelector('.sun-icon');
  const moonIcon = document.querySelector('.moon-icon');
  if (sunIcon) sunIcon.classList.toggle('hidden', state.isDark);
  if (moonIcon) moonIcon.classList.toggle('hidden', !state.isDark);

  showToast(state.isDark ? '🌙 Dark mode enabled' : '☀️ Light mode enabled');
}

// ══════════════════════════════════════════
// 🔔 NOTIFICATIONS
// ══════════════════════════════════════════
function toggleNotifications() {
  state.notifOpen = !state.notifOpen;
  const dd = document.getElementById('notifDropdown');
  if (state.notifOpen) {
    dd.style.display = 'block';
  } else {
    dd.style.display = 'none';
  }
}

function closeNotifications() {
  state.notifOpen = false;
  const dd = document.getElementById('notifDropdown');
  if (dd) dd.style.display = 'none';
}

function clearNotifications() {
  document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
  const dot = document.getElementById('notifDot');
  if (dot) dot.style.display = 'none';
  showToast('✅ All notifications marked as read');
  closeNotifications();
}

// Close notifs when clicking outside
document.addEventListener('click', (e) => {
  const wrapper = document.getElementById('notifWrapper');
  if (wrapper && !wrapper.contains(e.target)) closeNotifications();
});

// ══════════════════════════════════════════
// 📱 MOBILE MENU
// ══════════════════════════════════════════
function toggleMobileMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

// ══════════════════════════════════════════
// 🔐 AUTH FORMS
// ══════════════════════════════════════════
function switchAuthForm(type) {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const loginTab = document.getElementById('loginTab');
  const signupTab = document.getElementById('signupTab');

  if (type === 'login') {
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
  } else {
    signupForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
  }
}

async function loginUser(email, password) {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/v1/auth/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: email,   // ✅ KEY FIX
        password: password
      })
    });

    const data = await res.json();
    console.log("Login:", data);

    if (res.ok) {
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);

      showToast("✅ Login successful!");

      state.isLoggedIn = true;

      document.getElementById('authNavBtn').textContent = 'Logout';
      document.getElementById('authNavBtn').onclick = logoutUser;

      setTimeout(() => showSection('dashboard'), 600);

    } else {
      showToast("❌ " + (data.detail || "Login failed"));
    }

  } catch (err) {
    console.error(err);
    showToast("❌ Server error");
  }
}

function logoutUser() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");

  state.isLoggedIn = false;

  document.getElementById('authNavBtn').textContent = 'Login';
  document.getElementById('authNavBtn').onclick = () => showSection('auth');

  showToast('👋 Logged out successfully');
  setTimeout(() => showSection('home'), 400);
}

async function signupUser() {
  try {
    const firstName = document.getElementById("firstName").value.trim();
    const lastName = document.getElementById("lastName").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const state = document.getElementById("state").value;
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();

    console.log(firstName, lastName, email, password); // DEBUG

    if (!firstName || !lastName || !email || !password) {
      showToast("❌ Fill all required fields");
      return;
    }

    if (password !== confirmPassword) {
      showToast("❌ Password mismatch");
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/api/v1/auth/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: email,
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
        confirm_password: confirmPassword,
        phone: phone,
        state: state
      })
    });

    const data = await res.json();
    console.log("Response:", data);

    if (res.ok) {
      showToast("✅ Signup successful");
      switchAuthForm("login");
    } else {
      showToast("❌ " + Object.values(data).flat().join(", "));
    }

  } catch (err) {
    console.error(err);
    showToast("❌ Server error");
  }
}

// ══════════════════════════════════════════
// 📷 FILE UPLOAD
// ══════════════════════════════════════════
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) processFile(file);
}

function dragOver(event) {
  event.preventDefault();
  document.getElementById('uploadZone').classList.add('dragover');
}

function dragLeave(event) {
  document.getElementById('uploadZone').classList.remove('dragover');
}

function dropFile(event) {
  event.preventDefault();
  document.getElementById('uploadZone').classList.remove('dragover');
  const file = event.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) processFile(file);
  else showToast('⚠️ Please drop an image file only');
}

function processFile(file) {
  state.uploadedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = document.getElementById('previewImg');
    img.src = e.target.result;
    document.getElementById('previewFileName').textContent = file.name;
    document.getElementById('uploadIdle').classList.add('hidden');
    document.getElementById('uploadPreview').classList.remove('hidden');
  };
  reader.readAsDataURL(file);
  showToast(`📁 Image loaded: ${file.name}`);
}

function clearUpload() {
  state.uploadedFile = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('uploadIdle').classList.remove('hidden');
  document.getElementById('uploadPreview').classList.add('hidden');
}

function selectCrop(btn) {
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  state.selectedCrop = btn.textContent.trim();
}

// ══════════════════════════════════════════
// 🔬 AI ANALYSIS SIMULATION
// ══════════════════════════════════════════
function startAnalysis() {
  if (!state.uploadedFile) {
    showToast('⚠️ Please upload a crop image first!');
    return;
  }

  const btn = document.getElementById('analyzeBtn');
  const btnText = document.getElementById('analyzeBtnText');
  const spinner = document.getElementById('analyzeSpinner');
  const loadingEl = document.getElementById('analysisLoading');

  // Disable button & show spinner
  btn.disabled = true;
  btnText.textContent = 'Analyzing...';
  spinner.classList.remove('hidden');
  loadingEl.classList.remove('hidden');

  // Step animations
  const steps = [
    { id: 'lstep2', delay: 800, text: '✅ AI model running...' },
    { id: 'lstep3', delay: 1800, text: '✅ Generating heatmap...' },
    { id: 'lstep4', delay: 2600, text: '✅ Preparing results...' },
  ];

  const loadingTexts = [
    'Preprocessing image...',
    'Running deep neural network...',
    'Generating disease heatmap...',
    'Compiling results...'
  ];

  let textIdx = 0;
  const textInterval = setInterval(() => {
    textIdx = (textIdx + 1) % loadingTexts.length;
    const el = document.getElementById('loadingText');
    if (el) el.textContent = loadingTexts[textIdx];
  }, 750);

  steps.forEach(({ id, delay, text }) => {
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) {
        el.classList.remove('pending');
        el.textContent = text;
      }
    }, delay);
  });

  // Complete after 3.5s
  setTimeout(() => {
    clearInterval(textInterval);
    btn.disabled = false;
    btnText.textContent = '🔬 Analyze Now';
    spinner.classList.add('hidden');
    loadingEl.classList.add('hidden');

    // Reset steps
    document.getElementById('lstep2').classList.add('pending');
    document.getElementById('lstep2').textContent = '⏳ Running AI model...';
    document.getElementById('lstep3').classList.add('pending');
    document.getElementById('lstep3').textContent = '⏳ Generating heatmap...';
    document.getElementById('lstep4').classList.add('pending');
    document.getElementById('lstep4').textContent = '⏳ Preparing results...';

    showResults();
  }, 3500);
}

// ══════════════════════════════════════════
// 📈 SHOW RESULTS
// ══════════════════════════════════════════
const diseases = [
  { name: 'Wheat Leaf Rust', sci: 'Puccinia triticina', conf: 94, severity: 'High Severity', emoji: '⚠️',
    explanation: 'Wheat Leaf Rust is a fungal disease caused by Puccinia triticina. It manifests as orange-brown pustules on the leaf surface, reducing photosynthesis and grain yield by up to 30% if untreated.',
    treatment1: { name: 'Propiconazole 25% EC', desc: 'Apply 1 ml/litre of water. Spray on affected leaves twice at 15-day intervals.' },
    treatment2: { name: 'Neem Oil Spray', desc: '5 ml/litre as a preventive measure. Effective in early-stage infection.' }
  },
  { name: 'Tomato Late Blight', sci: 'Phytophthora infestans', conf: 89, severity: 'Critical', emoji: '🚨',
    explanation: 'Late Blight is one of the most destructive tomato diseases. Caused by the oomycete pathogen P. infestans, it spreads rapidly in cool, wet conditions and can destroy an entire crop.',
    treatment1: { name: 'Mancozeb 75% WP', desc: 'Apply 2g/litre every 7-10 days. Ensure complete coverage of foliage and fruit.' },
    treatment2: { name: 'Copper Oxychloride', desc: '3g/litre spray. Also works as a preventive fungicide especially before rainy season.' }
  },
  { name: 'Rice Blast', sci: 'Magnaporthe oryzae', conf: 91, severity: 'Moderate', emoji: '⚠️',
    explanation: 'Rice Blast is the most devastating disease of rice worldwide. The fungus can infect all above-ground parts of the rice plant causing leaf blast, collar rot, and neck rot.',
    treatment1: { name: 'Tricyclazole 75% WP', desc: 'Mix 0.6g/litre and spray during early tillering stage and at booting stage.' },
    treatment2: { name: 'Isoprothiolane', desc: '1.5 ml/litre. Excellent systemic fungicide effective against all blast stages.' }
  },
  { name: 'Healthy Crop', sci: 'No disease detected', conf: 98, severity: 'Healthy', emoji: '✅',
    explanation: 'Great news! Your crop appears healthy with no visible signs of disease. Continue with regular monitoring, proper irrigation, and balanced fertilization to maintain crop health.',
    treatment1: { name: 'Preventive Spray', desc: 'Monthly application of neem-based biopesticide to prevent future infections.' },
    treatment2: { name: 'Balanced Nutrition', desc: 'Ensure proper NPK balance. Healthy plants have stronger disease resistance.' }
  }
];

function showResults() {
  const disease = diseases[Math.floor(Math.random() * diseases.length)];

  // Set result image
  const previewSrc = document.getElementById('previewImg').src;
  document.getElementById('resultImg').src = previewSrc;
  document.getElementById('imgCaption').textContent = state.uploadedFile?.name || 'crop_image.jpg';

  // Set disease info
  document.getElementById('diseaseName').textContent = disease.name;
  document.getElementById('diseaseSci').textContent = disease.sci;
  document.getElementById('severityBadge').textContent = disease.severity;
  document.getElementById('confScore').textContent = disease.conf + '%';
  document.getElementById('confBar').style.setProperty('--conf', disease.conf + '%');
  document.getElementById('diseaseExplanation').textContent = disease.explanation;

  // Status icon
  document.querySelector('.disease-status-icon').textContent = disease.emoji;

  // Severity color
  const badge = document.getElementById('severityBadge');
  badge.style.cssText = disease.severity === 'Healthy'
    ? 'background: rgba(52,181,105,0.12); color: var(--green-600);'
    : disease.severity === 'Critical'
    ? 'background: rgba(226,64,64,0.15); color: #e24040;'
    : 'background: rgba(232,160,32,0.15); color: #e8a020;';

  // Treatment
  const treats = document.querySelectorAll('.treat-item');
  if (treats[0]) {
    treats[0].querySelector('strong').textContent = disease.treatment1.name;
    treats[0].querySelector('p').textContent = disease.treatment1.desc;
  }
  if (treats[1]) {
    treats[1].querySelector('strong').textContent = disease.treatment2.name;
    treats[1].querySelector('p').textContent = disease.treatment2.desc;
  }

  // Add to history
  state.historyData.unshift({
    id: Date.now(),
    crop: '📷', name: state.selectedCrop === 'Auto Detect' ? 'Unknown' : state.selectedCrop,
    disease: disease.name, status: disease.severity === 'Healthy' ? 'healthy' : 'disease',
    conf: disease.conf, date: new Date().toISOString().split('T')[0], type: 'other'
  });

  showToast('🔬 Analysis complete!');
  showSection('result');
}

// ══════════════════════════════════════════
// 🖼️ RESULT TABS (Original / Heatmap)
// ══════════════════════════════════════════
function switchResultTab(type, btn) {
  document.querySelectorAll('.rtab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  const overlay = document.getElementById('heatmapOverlay');
  if (type === 'heatmap') overlay.classList.remove('hidden');
  else overlay.classList.add('hidden');
}

// ══════════════════════════════════════════
// 📥 DOWNLOAD PDF (Simulated)
// ══════════════════════════════════════════
function downloadPDF() {
  showToast('📄 Generating PDF report...');
  setTimeout(() => showToast('✅ PDF downloaded: crop_analysis_report.pdf'), 1500);
}

// ══════════════════════════════════════════
// 📊 DASHBOARD ANIMATIONS
// ══════════════════════════════════════════
function initDashboardAnimations() {
  // Animate stat numbers
  document.querySelectorAll('.stat-num[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    let current = 0;
    const increment = Math.ceil(target / 40);
    const timer = setInterval(() => {
      current = Math.min(current + increment, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 30);
  });

  // Animate disease bars
  setTimeout(() => {
    document.querySelectorAll('.dis-bar').forEach(bar => {
      const w = bar.style.getPropertyValue('--w');
      bar.style.setProperty('--w', '0%');
      setTimeout(() => bar.style.setProperty('--w', w), 50);
    });
  }, 200);
}

// ══════════════════════════════════════════
// 📂 HISTORY RENDER & FILTER
// ══════════════════════════════════════════
function renderHistory(data = state.historyData) {
  const grid = document.getElementById('historyGrid');
  const noResults = document.getElementById('noResults');

  if (!grid) return;

  if (data.length === 0) {
    grid.innerHTML = '';
    noResults.classList.remove('hidden');
    return;
  }

  noResults.classList.add('hidden');
  grid.innerHTML = data.map(item => `
    <div class="hist-card" onclick="viewHistoryItem(${item.id})">
      <div class="hist-img">${item.crop}</div>
      <div class="hist-body">
        <h4>${item.name} — ${item.disease}</h4>
        <p class="hist-meta">📅 ${item.date} &nbsp;|&nbsp; 🔬 ${item.type}</p>
        <div class="hist-footer">
          <span class="badge ${item.status === 'disease' ? 'badge-red' : 'badge-green'}">
            ${item.status === 'disease' ? '⚠️ Disease' : '✅ Healthy'}
          </span>
          <span class="hist-conf">Confidence: ${item.conf}%</span>
        </div>
      </div>
    </div>
  `).join('');
}

function filterHistory() {
  const query = document.getElementById('historySearch')?.value.toLowerCase() || '';
  const filter = document.getElementById('historyFilter')?.value || 'all';

  const filtered = state.historyData.filter(item => {
    const matchQuery = item.name.toLowerCase().includes(query) || item.disease.toLowerCase().includes(query);
    const matchFilter = filter === 'all' || item.status === filter || item.type === filter;
    return matchQuery && matchFilter;
  });

  renderHistory(filtered);
}

function viewHistoryItem(id) {
  showToast('🔍 Loading analysis details...');
  // In a real app, this would load the specific analysis
  setTimeout(() => showSection('result'), 500);
}

// ══════════════════════════════════════════
// 🤖 CHATBOT
// ══════════════════════════════════════════
function toggleChatbot() {
  state.chatOpen = !state.chatOpen;
  const win = document.getElementById('chatWindow');
  const fabOpen = document.querySelector('.fab-icon-open');
  const fabClose = document.querySelector('.fab-icon-close');

  win.classList.toggle('hidden', !state.chatOpen);
  fabOpen.classList.toggle('hidden', state.chatOpen);
  fabClose.classList.toggle('hidden', !state.chatOpen);

  if (state.chatOpen) {
    document.getElementById('chatInput').focus();
  }
}

function chatKeydown(event) {
  if (event.key === 'Enter') sendChatMessage();
}

const botResponses = [
  "I can help you identify crop diseases! Upload a photo of the affected crop in the Upload section.",
  "Common symptoms of Wheat Leaf Rust include orange-brown pustules on leaves. It can reduce yield by up to 30%.",
  "For Tomato Late Blight, apply Mancozeb 75% WP at 2g/litre every 7-10 days for effective control.",
  "Rice Blast is most common during high humidity (>90%) and temperatures between 22-28°C. Ensure proper drainage.",
  "Prevention is better than cure! Regular field monitoring every 3-5 days during crop growth helps detect diseases early.",
  "Organic options include Neem oil (5ml/litre), Trichoderma-based biocontrol agents, and Pseudomonas fluorescens spray.",
  "You can track all your previous analyses in the History section. Use filters to find specific results.",
  "Our AI model has been trained on over 500,000 crop images covering 120+ diseases across 25 crop types."
];

let botRespIdx = 0;

function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;

  const messages = document.getElementById('chatMessages');

  // User message
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.textContent = msg;
  messages.appendChild(userDiv);
  input.value = '';

  // Typing indicator
  const typing = document.createElement('div');
  typing.className = 'chat-msg bot chat-typing';
  typing.innerHTML = '<span></span><span></span><span></span>';
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;

  // Bot response after delay
  setTimeout(() => {
    messages.removeChild(typing);
    const botDiv = document.createElement('div');
    botDiv.className = 'chat-msg bot';
    botDiv.textContent = botResponses[botRespIdx % botResponses.length];
    botRespIdx++;
    messages.appendChild(botDiv);
    messages.scrollTop = messages.scrollHeight;
  }, 1200);
}

// ══════════════════════════════════════════
// 🔔 TOAST NOTIFICATIONS
// ══════════════════════════════════════════
let toastTimer;
function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}

// ══════════════════════════════════════════
// 🚀 INIT ON LOAD
// ══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Show home section
  showSection('home');

  // Render initial history
  renderHistory();

  // Animate hero on load
  setTimeout(() => {
    document.querySelector('.hero-content')?.classList.add('visible');
  }, 100);

  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (window.scrollY > 20) nav.style.boxShadow = '0 4px 24px rgba(35, 100, 60, 0.12)';
    else nav.style.boxShadow = 'none';
  });

  // Check system dark mode preference
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    // Don't auto-apply; let user choose
  }

  // Welcome toast
  setTimeout(() => showToast('🌱 Welcome to Kishan Sathi! Upload your first crop image.'), 1000);
});

document.addEventListener("DOMContentLoaded", () => {
  
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", function(e) {
      e.preventDefault();

      const email = loginForm.querySelector("input[type='email']").value;
      const password = loginForm.querySelector("input[type='password']").value;

      loginUser(email, password);
    });
  }

});