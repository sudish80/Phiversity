// Phiversity Authentication System
let isLoggedIn = false;
let currentUser = null;

function showAuthModal(provider = null) {
  const modal = document.getElementById('authModal');
  if (modal) {
    modal.classList.add('active');
    if (provider === 'facebook') setTimeout(() => handleFacebookAuth(), 300);
    else if (provider === 'google') setTimeout(() => handleGoogleAuth(), 300);
    else if (provider === 'email') switchAuthTab('login');
  }
}

function closeAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) modal.classList.remove('active');
}

function switchAuthTab(tab) {
  const tabs = document.querySelectorAll('.auth-tab');
  tabs.forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const title = document.getElementById('authTitle');
  
  loginForm.classList.remove('active');
  signupForm.classList.remove('active');
  
  if (tab === 'login') {
    loginForm.classList.add('active');
    if (title) title.textContent = 'Welcome Back';
  } else {
    signupForm.classList.add('active');
    if (title) title.textContent = 'Join Phiversity';
  }
}

function handleEmailLogin() {
  const form = document.getElementById('loginForm');
  const email = form.querySelector('input[type="email"]').value;
  const password = form.querySelector('input[type="password"]').value;
  if (email && password) loginUser(email, 'email');
}

function handleEmailSignup() {
  const form = document.getElementById('signupForm');
  const name = form.querySelector('input[type="text"]').value;
  const email = form.querySelector('input[type="email"]').value;
  const password = form.querySelector('input[type="password"]').value;
  if (name && email && password) loginUser(email, 'email', name);
}

function handleEmailAuth() {
  showAuthModal('email');
}

function handleFacebookAuth() {
  loginUser('user@facebook.com', 'facebook', 'Facebook User');
}

function handleGoogleAuth() {
  loginUser('user@google.com', 'google', 'Google User');
}

function loginUser(email, provider, name = 'User') {
  isLoggedIn = true;
  currentUser = { email, provider, name, loginTime: new Date() };
  localStorage.setItem('phiversity_user', JSON.stringify(currentUser));
  closeAuthModal();
  showToast(`Welcome ${name}! 🎉`, 'success');
  updateAuthUI();
}

function logoutUser() {
  isLoggedIn = false;
  currentUser = null;
  localStorage.removeItem('phiversity_user');
  showToast('Logged out successfully', 'success');
  updateAuthUI();
}

function updateAuthUI() {
  const authTrigger = document.querySelector('.auth-trigger');
  if (!authTrigger) return;
  
  if (isLoggedIn && currentUser) {
    const firstName = currentUser.name.split(' ')[0];
    authTrigger.innerHTML = `<div class="auth-btn-group" style="gap:8px;">
      <div style="display:flex;align-items:center;gap:8px;padding:0 12px;color:var(--text-secondary);font-size:12px;">👤 ${firstName}</div>
      <button class="auth-mini-btn" onclick="logoutUser()" title="Logout">🚪</button>
    </div>`;
  } else {
    authTrigger.innerHTML = `<div class="auth-btn-group">
      <button class="auth-mini-btn email" onclick="showAuthModal('email')" title="Sign in with Email">✉️</button>
      <button class="auth-mini-btn facebook" onclick="showAuthModal('facebook')" title="Sign in with Facebook">f</button>
      <button class="auth-mini-btn google" onclick="showAuthModal('google')" title="Sign in with Google">G</button>
    </div>`;
  }
}

// Initialize on page load
function initializeAuth() {
  const savedUser = localStorage.getItem('phiversity_user');
  if (savedUser) {
    try {
      currentUser = JSON.parse(savedUser);
      isLoggedIn = true;
      updateAuthUI();
    } catch (e) {
      console.log('Could not restore user session');
    }
  }
  
  // Close modal on background click
  const modal = document.getElementById('authModal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target.id === 'authModal') closeAuthModal();
    });
  }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeAuth);
window.addEventListener('load', initializeAuth);
