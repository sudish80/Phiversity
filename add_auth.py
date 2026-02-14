#!/usr/bin/env python3
import re

# Read the original file
with open('web/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert auth styles before the Animations comment
auth_styles = '''
    /* Auth Modal Styles */
    .auth-modal {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      z-index: 2000;
      align-items: center;
      justify-content: center;
      animation: fadeIn 0.3s ease;
    }

    .auth-modal.active {
      display: flex;
    }

    .auth-modal-content {
      background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
      border: 2px solid var(--border);
      border-radius: 24px;
      padding: 48px;
      max-width: 450px;
      width: 90%;
      box-shadow: 
        0 40px 100px rgba(0, 0, 0, 0.5),
        0 20px 60px rgba(99, 102, 241, 0.3),
        inset 0 2px 30px rgba(255, 255, 255, 0.1);
      animation: slideUp 0.4s ease;
      position: relative;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(40px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .auth-close {
      position: absolute;
      top: 20px;
      right: 20px;
      background: rgba(99, 102, 241, 0.2);
      border: none;
      color: var(--text-primary);
      font-size: 24px;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .auth-close:hover {
      background: rgba(99, 102, 241, 0.4);
      transform: rotate(90deg);
    }

    .auth-header {
      text-align: center;
      margin-bottom: 32px;
    }

    .auth-header h2 {
      font-size: 28px;
      margin-bottom: 8px;
      background: linear-gradient(135deg, var(--primary), var(--secondary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .auth-header p {
      color: var(--text-secondary);
      font-size: 14px;
    }

    .auth-tabs {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      border-bottom: 2px solid var(--border);
    }

    .auth-tab {
      flex: 1;
      padding: 12px;
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s ease;
      border-bottom: 3px solid transparent;
      margin-bottom: -2px;
    }

    .auth-tab.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
    }

    .auth-form {
      display: none;
    }

    .auth-form.active {
      display: block;
      animation: fadeIn 0.3s ease;
    }

    .auth-input-group {
      margin-bottom: 16px;
    }

    .auth-input {
      width: 100%;
      padding: 12px 16px;
      background: rgba(15, 15, 35, 0.8);
      border: 2px solid var(--border);
      border-radius: 10px;
      color: var(--text-primary);
      font-size: 14px;
      font-family: inherit;
      transition: all 0.3s ease;
    }

    .auth-input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    }

    .auth-input::placeholder {
      color: var(--text-secondary);
    }

    .auth-button {
      width: 100%;
      padding: 12px 24px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      border: none;
      border-radius: 10px;
      color: white;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s ease;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .auth-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
    }

    .auth-divider {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 24px 0;
    }

    .auth-divider::before,
    .auth-divider::after {
      content: '';
      flex: 1;
      height: 1px;
      background: var(--border);
    }

    .auth-divider-text {
      color: var(--text-secondary);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .auth-social-buttons {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
      margin-bottom: 16px;
    }

    .auth-social-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px;
      background: rgba(99, 102, 241, 0.1);
      border: 2px solid var(--border);
      border-radius: 12px;
      color: var(--text-primary);
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 24px;
      position: relative;
      overflow: hidden;
    }

    .auth-social-btn::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
      transition: left 0.5s ease;
    }

    .auth-social-btn:hover {
      border-color: var(--primary);
      background: rgba(99, 102, 241, 0.2);
      transform: translateY(-4px);
      box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
    }

    .auth-social-btn:hover::before {
      left: 100%;
    }

    .auth-social-btn.email { color: #ff6b6b; }
    .auth-social-btn.facebook { color: #1877f2; }
    .auth-social-btn.google { color: #ea4335; }

    .auth-toggle {
      text-align: center;
      color: var(--text-secondary);
      font-size: 14px;
      margin-top: 16px;
    }

    .auth-toggle a {
      color: var(--primary);
      cursor: pointer;
      text-decoration: none;
      font-weight: 600;
      transition: color 0.3s ease;
    }

    .auth-toggle a:hover {
      color: var(--secondary);
    }

    .auth-trigger {
      position: fixed;
      bottom: 30px;
      right: 30px;
      display: flex;
      gap: 10px;
      align-items: center;
      z-index: 100;
      animation: slideInRight 0.5s ease;
    }

    .auth-btn-group {
      display: flex;
      gap: 10px;
      background: rgba(30, 30, 60, 0.9);
      backdrop-filter: blur(10px);
      padding: 12px 16px;
      border-radius: 50px;
      border: 2px solid var(--border);
      box-shadow: 0 10px 40px rgba(99, 102, 241, 0.2);
    }

    .auth-mini-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: none;
      cursor: pointer;
      font-size: 18px;
      transition: all 0.3s ease;
      background: rgba(99, 102, 241, 0.1);
    }

    .auth-mini-btn:hover {
      background: linear-gradient(135deg, var(--primary), var(--accent));
      transform: scale(1.1);
    }

    .auth-mini-btn.email { color: #ff6b6b; }
    .auth-mini-btn.facebook { color: #1877f2; }
    .auth-mini-btn.google { color: #ea4335; }

    @keyframes slideInRight {
      from { opacity: 0; transform: translateX(30px); }
      to { opacity: 1; transform: translateX(0); }
    }
'''

content = content.replace('    /* Animations */', auth_styles + '\n    /* Animations */')

# Insert auth modal HTML before loading overlay
auth_modal_html = '''  <!-- Auth Modal -->
  <div id="authModal" class="auth-modal">
    <div class="auth-modal-content">
      <button class="auth-close" onclick="closeAuthModal()">✕</button>
      <div class="auth-header">
        <h2 id="authTitle">Welcome Back</h2>
        <p>Sign in or create your account to save your videos</p>
      </div>
      <div class="auth-tabs">
        <button class="auth-tab active" onclick="switchAuthTab('login')">Sign In</button>
        <button class="auth-tab" onclick="switchAuthTab('signup')">Sign Up</button>
      </div>
      <form class="auth-form active" id="loginForm">
        <div class="auth-input-group">
          <input type="email" class="auth-input" placeholder="Email address" required>
        </div>
        <div class="auth-input-group">
          <input type="password" class="auth-input" placeholder="Password" required>
        </div>
        <button type="button" class="auth-button" onclick="handleEmailLogin()">Sign In with Email</button>
      </form>
      <form class="auth-form" id="signupForm">
        <div class="auth-input-group">
          <input type="text" class="auth-input" placeholder="Full name" required>
        </div>
        <div class="auth-input-group">
          <input type="email" class="auth-input" placeholder="Email address" required>
        </div>
        <div class="auth-input-group">
          <input type="password" class="auth-input" placeholder="Password" required>
        </div>
        <button type="button" class="auth-button" onclick="handleEmailSignup()">Create Account</button>
      </form>
      <div class="auth-divider">
        <span class="auth-divider-text">Or continue with</span>
      </div>
      <div class="auth-social-buttons">
        <button type="button" class="auth-social-btn email" onclick="handleEmailAuth()" title="Email">✉️</button>
        <button type="button" class="auth-social-btn facebook" onclick="handleFacebookAuth()" title="Facebook">f</button>
        <button type="button" class="auth-social-btn google" onclick="handleGoogleAuth()" title="Google">G</button>
      </div>
      <div class="auth-toggle">
        <span id="toggleText">Don't have an account? <a onclick="switchAuthTab('signup')">Sign up</a></span>
      </div>
    </div>
  </div>

  <!-- Auth Buttons (Bottom Right) -->
  <div class="auth-trigger">
    <div class="auth-btn-group">
      <button class="auth-mini-btn email" onclick="showAuthModal('email')" title="Sign in with Email">✉️</button>
      <button class="auth-mini-btn facebook" onclick="showAuthModal('facebook')" title="Sign in with Facebook">f</button>
      <button class="auth-mini-btn google" onclick="showAuthModal('google')" title="Sign in with Google">G</button>
    </div>
  </div>

'''

content = content.replace('  <!-- Loading Overlay -->', auth_modal_html + '  <!-- Loading Overlay -->')

# Insert auth JavaScript after pollInterval initialization
auth_js = '''    let isLoggedIn = false;
    let currentUser = null;

    function showAuthModal(provider = null) {
      document.getElementById('authModal').classList.add('active');
      if (provider === 'facebook') setTimeout(() => handleFacebookAuth(), 300);
      else if (provider === 'google') setTimeout(() => handleGoogleAuth(), 300);
      else if (provider === 'email') switchAuthTab('login');
    }

    function closeAuthModal() {
      document.getElementById('authModal').classList.remove('active');
    }

    function switchAuthTab(tab) {
      document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById('loginForm').classList.remove('active');
      document.getElementById('signupForm').classList.remove('active');
      if (tab === 'login') {
        document.getElementById('loginForm').classList.add('active');
        document.getElementById('authTitle').textContent = 'Welcome Back';
        document.getElementById('toggleText').innerHTML = 'Don\\'t have an account? <a onclick="switchAuthTab(\\'signup\\')">Sign up</a>';
      } else {
        document.getElementById('signupForm').classList.add('active');
        document.getElementById('authTitle').textContent = 'Join Phiversity';
        document.getElementById('toggleText').innerHTML = 'Already have an account? <a onclick="switchAuthTab(\\'login\\')">Sign in</a>';
      }
    }

    function handleEmailLogin() {
      const email = document.querySelector('#loginForm .auth-input[type="email"]').value;
      const password = document.querySelector('#loginForm .auth-input[type="password"]').value;
      if (email && password) loginUser(email, 'email');
    }

    function handleEmailSignup() {
      const name = document.querySelector('#signupForm .auth-input[type="text"]').value;
      const email = document.querySelector('#signupForm .auth-input[type="email"]').value;
      const password = document.querySelector('#signupForm .auth-input[type="password"]').value;
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
      if (isLoggedIn && currentUser) {
        authTrigger.innerHTML = '<div class="auth-btn-group" style="gap: 8px;"><div style="display: flex; align-items: center; gap: 8px; padding: 0 12px; color: var(--text-secondary); font-size: 12px;">👤 ' + currentUser.name.split(' ')[0] + '</div><button class="auth-mini-btn" onclick="logoutUser()" title="Logout">🚪</button></div>';
      } else {
        authTrigger.innerHTML = '<div class="auth-btn-group"><button class="auth-mini-btn email" onclick="showAuthModal(\\'email\\')" title="Sign in with Email">✉️</button><button class="auth-mini-btn facebook" onclick="showAuthModal(\\'facebook\\')" title="Sign in with Facebook">f</button><button class="auth-mini-btn google" onclick="showAuthModal(\\'google\\')" title="Sign in with Google">G</button></div>';
      }
    }

'''

content = content.replace('    let currentJobId = null;\n    let pollInterval = null;', 
                          'let currentJobId = null;\n    let pollInterval = null;\n\n' + auth_js)

# Insert event listeners
events_js = '''    // Close auth modal on background click
    document.getElementById('authModal').addEventListener('click', (e) => {
      if (e.target.id === 'authModal') closeAuthModal();
    });

    // Load user from localStorage on page load
    window.addEventListener('load', () => {
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
    });

'''

content = content.replace('    // Custom prompt toggle', events_js + '    // Custom prompt toggle')

# Write the updated file
with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Authentication UI added successfully!")
print("✓ Features:")
print("  - Email login/signup")
print("  - Facebook authentication (demo)")
print("  - Google authentication (demo)")
print("  - Icons at bottom right corner (bottom-right fixed position)")
print("  - User session persistence with localStorage")
print("  - Logout functionality with icon change")
print("  - Beautiful modal with glassmorphism design")
