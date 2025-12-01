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
      
      // Emit login event with user data
      emit('login', {
        email: formData.value.email,
        username: formData.value.email,
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
</style>
