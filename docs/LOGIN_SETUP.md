# Phiversity 3D Login Interface

## Overview
A modern, realistic, and user-friendly 3D login and sign-up interface with:
- ✨ **3D Animated Background** - Subtle Three.js animations with floating shapes and dynamic lighting
- 🎨 **Glassmorphism Design** - Modern frosted glass effect cards
- 🔄 **Smooth Transitions** - Animated form switching between login and signup
- 📱 **Fully Responsive** - Works perfectly on desktop, tablet, and mobile
- 🔐 **Professional Validation** - Real-time field validation with error messages
- 🔒 **Password Features** - Show/hide toggle, strength indicator, confirmation matching
- 📢 **Toast Notifications** - Professional notification system instead of browser alerts
- ✅ **User-Friendly UX** - Inline error messages, loading indicators, accessibility support

## New Features (v2.0)

### ✨ Enhanced Form Validation
- Real-time email validation
- Password strength indicator with visual feedback
  - Weak / Fair / Good / Strong levels
  - Color-coded strength bar (red → orange → yellow → green)
- Password confirmation matching
- Full name validation (first & last name required)
- Inline error messages below each field
- Field highlighting on validation errors

### 🔐 Security & Usability
- **Show/Hide Password Toggle** - Click eye icon to reveal/hide password
- **Password Requirements** - Clear feedback on password complexity
- **Async Form Handling** - Simulated API calls with loading spinners
- **No Browser Alerts** - Professional toast notifications instead

### 🎯 Toast Notification System
Four types of notifications:
- ✅ **Success** - Green background, checkmark icon
- ❌ **Error** - Red background, X icon
- ⚠️ **Warning** - Orange background, warning icon
- ℹ️ **Info** - Blue background, info icon

Auto-dismisses after 4 seconds (customizable)

### 📊 Password Strength Indicator
Shows real-time feedback:
- 6+ chars = Weak
- 8+ chars = Fair
- + Uppercase = Good
- + Numbers = Very Good
- + Special chars = Strong

### 🎨 Responsive Design
- Desktop optimized (400px card width)
- Tablet friendly (90% max-width)
- Mobile optimized (95% width, adjusted padding)
- Touch-friendly button sizes
- Proper spacing on small screens

## Features Included

### Login Form
- ✅ Email validation (real-time feedback)
- ✅ Password field with show/hide toggle
- ✅ "Remember me" checkbox
- ✅ "Forgot Password" link (opens reset flow)
- ✅ Sign in with Google/Facebook
- ✅ Skip for now (guest mode)
- ✅ Link to switch to signup
- ✅ Error messages for all fields

### Sign Up Form
- ✅ Full name validation (min 2 words)
- ✅ Email validation
- ✅ Password with strength indicator
- ✅ Password confirmation matching
- ✅ Show/hide toggles for both passwords
- ✅ Sign up with Google/Facebook
- ✅ Skip for now (guest mode)
- ✅ Link to switch back to login
- ✅ Clear error feedback

### Professional UI Elements
- 🌌 Subtle 3D background animations
- 📝 Real-time field validation
- ⚙️ Loading spinners on form submission
- 🔔 Non-intrusive toast notifications
- 🎭 Smooth form transitions
- 📍 Footer links (Terms, Privacy, Help)



## File Location
```
web/login.html
```

## How to Use

### Option 1: As Standalone Page
Open directly in browser:
```
file:///path-to-project/web/login.html
```

### Option 2: Integrate with FastAPI Server
Add this route to `scripts/server/app.py`:

```python
@app.get("/login")
async def login_page():
    login_path = ROOT / "web" / "login.html"
    if login_path.exists():
        return FileResponse(login_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Login page not found")
```

Then visit: `http://localhost:8001/login`

### Option 3: As Default Landing Page
Update `scripts/server/app.py` to serve login.html at root:

```python
@app.get("/")
async def root():
    login_path = ROOT / "web" / "login.html"
    if login_path.exists():
        return FileResponse(login_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Login page not found")
```

Then navigate to: `http://localhost:8001/`

## Customization

### Colors
Edit the gradient in the CSS:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
```

### Logo Text
Change "Phiversity" in the HTML:
```html
<div class="logo">Your App Name</div>
<div class="subtitle">Your Tagline</div>
```

### Form Fields
Add/remove form fields as needed in the `<form>` elements

### 3D Animation Speed
Adjust time increment in animation loop:
```javascript
time += 0.01;  // Increase for faster animation, decrease for slower
```

### Particle Count
Modify `particlesCount` value (more = slower but prettier):
```javascript
const particlesCount = 5000;  // Adjust as needed
```

## Integration with Backend

### Connect Login to Backend API
Replace form submission handlers in the script section:

```javascript
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            // Store token, redirect, etc.
            alert('Login successful!');
        }
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
});
```

### Add Authentication Endpoints
Add to `scripts/server/app.py`:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

@app.post("/api/login")
async def login(email: str, password: str):
    # Verify credentials (implement your auth logic)
    # Create JWT token
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/signup")
async def signup(name: str, email: str, password: str):
    # Create user in database
    # Return success or error
    return {"message": "Account created successfully"}
```

## Browser Compatibility
- ✅ Chrome/Edge (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)
- ✅ Mobile Browsers (iOS Safari, Chrome Mobile)

## Performance Notes
- Uses hardware-accelerated WebGL rendering
- Optimized particle system with vertex colors
- Efficient animation loop using requestAnimationFrame
- ~60 FPS on modern devices

## Dependencies
- **Three.js** (v128) - loaded from CDN
  - No installation needed, loaded automatically from CDN

## Troubleshooting

**3D Background not showing?**
- Check browser console for errors
- Ensure Three.js CDN is accessible
- Try disabling browser extensions

**Forms not responding?**
- Check browser console for JavaScript errors
- Ensure DOM elements have correct IDs

**Performance issues?**
- Reduce `particlesCount` from 5000 to 2000-3000
- Reduce `shapes` array loop from 20 to 10
- Disable some animations

## New Features (v2.0)

### ✨ Enhanced Form Validation
- Real-time email validation with visual feedback
- **Password strength indicator**:
  - Weak: 0-6 chars (red)
  - Fair: 7-8 chars (orange)
  - Good: + uppercase/numbers (yellow)
  - Strong: + special chars (green)
- Password confirmation matching verification
- Full name validation (min 2 words)
- **Inline error messages** on each field
- **Field highlighting** when validation fails
- Errors clear when user fixes input

### 🔐 Password Features
- **Show/Hide Toggle**: Click eye icon (👁️ → 🙈) to reveal/hide password
- **Strength Bar**: Visual progress indicator during signup
- **Confirmation Matching**: Prevents typos
- **Min 6 characters**: Strong validation rules
- **Special char support**: Allow @, !, #, $, %, ^, &, * in passwords

### 📢 Professional Notifications
Replaced all browser `alert()` with elegant toast notifications:

**Success (Green)**
```
✅ Login successful! Welcome to Phiversity! 🎓
✅ Account created successfully!
✅ Password reset link sent to email
```

**Error (Red)**
```
❌ Passwords do not match
❌ Please enter a valid email
❌ Login failed. Please try again.
```

**Warning (Orange)**
```
⚠️ Please fix the errors above
⚠️ Please enter your email address first
```

**Info (Blue)**
```
ℹ️ Redirecting to Google login...
ℹ️ Continuing as guest...
ℹ️ Help & Support - Contact...
```

### ✅ Form Validation Points

**Login Form**
```
❌ Email is required
❌ Please enter a valid email
❌ Password is required
```

**Signup Form**
```
❌ Full name is required
❌ Please enter your first and last name
❌ Email is required
❌ Please enter a valid email
❌ Password is required
❌ Password must be at least 6 characters
❌ Passwords do not match
```

### 🎯 User Experience Improvements
- **Loading Indicators**: Spinning dot animation during form submission
- **Disabled Buttons**: Prevents double-click submission
- **Auto-Dismissing Notifications**: Toast messages auto-hide after 4 seconds
- **Smooth Transitions**: 0.6s animations between login/signup forms
- **Field Focus Management**: Better keyboard navigation
- **Mobile Optimized**: Touch-friendly buttons and spacing

### 📱 Responsive Design
- **Desktop**: 400px card centered, full 3D animations
- **Tablet**: 90% width, responsive padding
- **Mobile**: 95% width, optimized touch targets (44px+), reduced animations
- **Landscape**: Adjusted height handling
- **Footer Links**: Links for Terms, Privacy, Help

## Features Summary

| Feature | Login | Signup | Notes |
|---------|-------|--------|-------|
| Email validation | ✅ | ✅ | Real-time |
| Password field | ✅ | ✅ | Show/hide toggle |
| Password strength | ❌ | ✅ | With visual bar |
| Confirm password | ❌ | ✅ | Matching check |
| Name field | ❌ | ✅ | 2+ words required |
| Remember me | ✅ | ❌ | Checkbox |
| Forgot password | ✅ | ❌ | Link |
| Social login | ✅ | ✅ | Google + Facebook |
| Error messages | ✅ | ✅ | Inline feedback |
| Loading state | ✅ | ✅ | Spinner |
| Toast notifications | ✅ | ✅ | 4 types |

## How It Works

### 1. User enters email
```
Validation: format check
Feedback: inline error or clear ✓
```

### 2. User enters password  
```
On Login:
- Validation: not empty
- Feedback: inline error

On Signup:
- Strength check: weak → strong
- Visual bar: 0-100% filled
- Color changes: red → green
```

### 3. Form submission
```
- Validates all fields
- Shows spinner
- Simulates API call (1.5s)
- Shows success/error toast
- Clears form on success
```

### 4. Form switching
```
- Slides out current form (left)
- Slides in new form (right)
- Smooth 0.6s transition
- Maintains state (if needed)
```

## Future Enhancements
- [ ] Two-factor authentication (2FA) UI
- [ ] Email verification flow
- [ ] Password reset with token validation
- [ ] User profile picture upload
- [ ] Phone number field (optional)
- [ ] Terms & conditions modal
- [ ] CAPTCHA integration (reCAPTCHA)
- [ ] Dark/Light mode toggle
- [ ] Language selector (i18n)
- [ ] Rate limiting indicator
- [ ] Account lockout notification
- [ ] Session management
