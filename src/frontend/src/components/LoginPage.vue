<script setup>
import { SignIn, SignUp, SignedIn, SignedOut, UserButton } from '@clerk/vue'
import { ref } from 'vue'

const showSignUp = ref(false)

const emit = defineEmits(['login'])

// When user signs in successfully via Clerk, emit login event
const handleClerkSignIn = () => {
  emit('login', { authenticated: true })
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>Welcome to Depict-AI</h1>
        <p>Sign in to access your projects</p>
      </div>

      <!-- Show when user is NOT signed in -->
      <SignedOut>
        <div class="clerk-auth-wrapper">
          <!-- Toggle between Sign In and Sign Up -->
          <SignIn 
            v-if="!showSignUp"
            :appearance="{
              elements: {
                rootBox: 'mx-auto',
                card: 'shadow-none'
              }
            }"
            @clerk:signin="handleClerkSignIn"
          />
          <SignUp 
            v-else
            :appearance="{
              elements: {
                rootBox: 'mx-auto',
                card: 'shadow-none'
              }
            }"
            @clerk:signup="handleClerkSignIn"
          />
          
          <div class="toggle-mode">
            <button 
              @click="showSignUp = !showSignUp"
              class="toggle-button"
            >
              {{ showSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up" }}
            </button>
          </div>
        </div>
      </SignedOut>

      <!-- Show when user IS signed in -->
      <SignedIn>
        <div class="signed-in-state">
          <p>You're already signed in!</p>
          <UserButton 
            :appearance="{
              elements: {
                rootBox: 'mx-auto'
              }
            }"
          />
        </div>
      </SignedIn>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary));
  padding: 2rem;
}

.login-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 480px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.login-header p {
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.clerk-auth-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.toggle-mode {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.toggle-button {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 0.95rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  transition: all 0.2s ease;
}

.toggle-button:hover {
  text-decoration: underline;
  opacity: 0.8;
}

.signed-in-state {
  text-align: center;
  padding: 2rem;
}

.signed-in-state p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: var(--color-text-secondary);
}
</style>
