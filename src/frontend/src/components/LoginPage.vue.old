<script setup>
import { ref } from 'vue';
import { User, Mail, Lock, Eye, EyeOff } from 'lucide-vue-next';

const emit = defineEmits(['login']);

const isLogin = ref(true);
const showPassword = ref(false);
const formData = ref({
  email: '',
  password: '',
  username: '',
  confirmPassword: ''
});
const errors = ref({});
const loading = ref(false);

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  errors.value = {};
  formData.value = {
    email: '',
    password: '',
    username: '',
    confirmPassword: ''
  };
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const validateForm = () => {
  errors.value = {};
  
  if (!formData.value.email) {
    errors.value.email = 'Email is required';
  } else if (!/\S+@\S+\.\S+/.test(formData.value.email)) {
    errors.value.email = 'Email is invalid';
  }
  
  if (!formData.value.password) {
    errors.value.password = 'Password is required';
  } else if (formData.value.password.length < 6) {
    errors.value.password = 'Password must be at least 6 characters';
  }
  
  if (!isLogin.value) {
    if (!formData.value.username) {
      errors.value.username = 'Username is required';
    }
    
    if (formData.value.password !== formData.value.confirmPassword) {
      errors.value.confirmPassword = 'Passwords do not match';
    }
  }
  
  return Object.keys(errors.value).length === 0;
};

const hashPassword = async (password) => {
  // Simple hash function - in production, use a proper hashing library
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
};

const handleSubmit = async () => {
  if (!validateForm()) return;
  
  loading.value = true;
  
  try {
    const hashedPassword = await hashPassword(formData.value.password);
    
    if (isLogin.value) {
      // Login
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.value.email, // Backend expects username field
          hashed_password: hashedPassword
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      
      // Store JWT token
      localStorage.setItem('token', data.access_token);
      
      // Emit login event with user data
      emit('login', {
        email: formData.value.email,
        username: data.username || formData.value.email,
        user_id: data.user_id
      });
    } else {
      // Sign up
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.value.username,
          email: formData.value.email,
          hashed_password: hashedPassword,
          permission: 'view only' // Default permission
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signup failed');
      }
      
      const data = await response.json();
      
      // Automatically log in after successful signup
      emit('login', {
        email: formData.value.email,
        username: formData.value.username,
        user_id: data.user_id
      });
    }
  } catch (error) {
    errors.value.general = error.message || 'An error occurred. Please try again.';
  } finally {
    loading.value = false;
  }
};

// OAuth2 Social Login Handlers
const handleGoogleLogin = () => {
  // Redirect to Google OAuth2 endpoint
  window.location.href = 'http://localhost:8000/auth/google/login';
};

const handleMicrosoftLogin = () => {
  // Redirect to Microsoft OAuth2 endpoint
  window.location.href = 'http://localhost:8000/auth/microsoft/login';
};

const handleGitHubLogin = () => {
  // Redirect to GitHub OAuth2 endpoint
  window.location.href = 'http://localhost:8000/auth/github/login';
};
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Depict AI</h1>
        <p class="auth-subtitle">
          {{ isLogin ? 'Welcome back' : 'Create your account' }}
        </p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="errors.general" class="error-message general">
          {{ errors.general }}
        </div>
        
        <!-- Username (Sign up only) -->
        <div v-if="!isLogin" class="form-group">
          <label class="form-label">Username</label>
          <div class="input-wrapper">
            <User :size="20" class="input-icon" />
            <input
              v-model="formData.username"
              type="text"
              class="form-input"
              :class="{ 'error': errors.username }"
              placeholder="Enter your username"
            />
          </div>
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>
        
        <!-- Email -->
        <div class="form-group">
          <label class="form-label">Email</label>
          <div class="input-wrapper">
            <Mail :size="20" class="input-icon" />
            <input
              v-model="formData.email"
              type="email"
              class="form-input"
              :class="{ 'error': errors.email }"
              placeholder="Enter your email"
            />
          </div>
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>
        
        <!-- Password -->
        <div class="form-group">
          <label class="form-label">Password</label>
          <div class="input-wrapper">
            <Lock :size="20" class="input-icon" />
            <input
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ 'error': errors.password }"
              placeholder="Enter your password"
            />
            <button
              type="button"
              @click="togglePasswordVisibility"
              class="password-toggle"
            >
              <Eye v-if="!showPassword" :size="20" />
              <EyeOff v-if="showPassword" :size="20" />
            </button>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>
        
        <!-- Confirm Password (Sign up only) -->
        <div v-if="!isLogin" class="form-group">
          <label class="form-label">Confirm Password</label>
          <div class="input-wrapper">
            <Lock :size="20" class="input-icon" />
            <input
              v-model="formData.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :class="{ 'error': errors.confirmPassword }"
              placeholder="Confirm your password"
            />
          </div>
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>
        
        <!-- Forgot Password (Login only) -->
        <div v-if="isLogin" class="forgot-password">
          <a href="#" class="forgot-link">Forgot password?</a>
        </div>
        
        <!-- Submit Button -->
        <button type="submit" class="submit-button" :disabled="loading">
          <span v-if="!loading">{{ isLogin ? 'Sign In' : 'Sign Up' }}</span>
          <span v-else class="loading-spinner"></span>
        </button>
        
        <!-- Divider -->
        <div class="divider">
          <span>OR</span>
        </div>
        
        <!-- OAuth2 Social Login Buttons -->
        <div class="social-login">
          <button type="button" @click="handleGoogleLogin" class="social-button google" :disabled="loading">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>
          
          <button type="button" @click="handleMicrosoftLogin" class="social-button microsoft" :disabled="loading">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#f25022" d="M11.4 11.4H2V2h9.4v9.4z"/>
              <path fill="#00a4ef" d="M22 11.4h-9.4V2H22v9.4z"/>
              <path fill="#7fba00" d="M11.4 22H2v-9.4h9.4V22z"/>
              <path fill="#ffb900" d="M22 22h-9.4v-9.4H22V22z"/>
            </svg>
            Continue with Microsoft
          </button>
          
          <button type="button" @click="handleGitHubLogin" class="social-button github" :disabled="loading">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#181717" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            Continue with GitHub
          </button>
        </div>
        
        <!-- Toggle Mode -->
        <div class="toggle-mode">
          <span>{{ isLogin ? "Don't have an account?" : 'Already have an account?' }}</span>
          <button type="button" @click="toggleMode" class="toggle-link">
            {{ isLogin ? 'Sign Up' : 'Sign In' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #8b9ffb 0%, #ffffff 100%);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-title {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.auth-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: #95a5a6;
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 12px 12px 12px 44px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  outline: none;
}

.form-input:focus {
  border-color: #667eea;
}

.form-input.error {
  border-color: #e74c3c;
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #95a5a6;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #667eea;
}

.error-message {
  font-size: 12px;
  color: #e74c3c;
}

.error-message.general {
  padding: 12px;
  background: #fee;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  text-align: center;
}

.forgot-password {
  text-align: right;
  margin-top: -8px;
}

.forgot-link {
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

.submit-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg,  #8b9ffb 0%, #5b79ff 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 8px;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.toggle-mode {
  text-align: center;
  font-size: 14px;
  color: #7f8c8d;
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.toggle-link {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
}

.toggle-link:hover {
  text-decoration: underline;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 24px 0 20px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0e0e0;
}

.divider span {
  padding: 0 16px;
  font-size: 13px;
  color: #95a5a6;
  font-weight: 500;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.social-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.social-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.social-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.social-button.google {
  color: #444;
}

.social-button.google:hover:not(:disabled) {
  border-color: #4285F4;
  background: #f8fbff;
}

.social-button.microsoft {
  color: #444;
}

.social-button.microsoft:hover:not(:disabled) {
  border-color: #00a4ef;
  background: #f0f9ff;
}

.social-button.github {
  color: #444;
}

.social-button.github:hover:not(:disabled) {
  border-color: #181717;
  background: #f6f8fa;
}

.social-button svg {
  flex-shrink: 0;
}
</style>
