<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <i class="bi bi-person-plus-fill text-primary display-3"></i>
                <h2 class="mt-3">Create Account</h2>
                <p class="text-muted">Join us today</p>
              </div>
              
              <div 
                v-if="error" 
                class="alert alert-danger alert-dismissible fade show" 
                role="alert"
              >
                {{ error }}
                <button 
                  type="button" 
                  class="btn-close" 
                  @click="error = ''"
                ></button>
              </div>
              
              <div 
                v-if="success" 
                class="alert alert-success" 
                role="alert"
              >
                {{ success }}
              </div>
              
              <form @submit.prevent="handleRegister">
                <div class="mb-3">
                  <label for="username" class="form-label">Username *</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    id="username"
                    v-model="formData.username"
                    required
                    placeholder="Choose a username"
                  >
                </div>
                
                <div class="mb-3">
                  <label for="email" class="form-label">Email *</label>
                  <input 
                    type="email" 
                    class="form-control form-control-lg" 
                    id="email"
                    v-model="formData.email"
                    required
                    placeholder="your.email@example.com"
                  >
                  <div class="form-text">
                    We'll send booking confirmations and reports here
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="password" class="form-label">Password *</label>
                  <input 
                    type="password" 
                    class="form-control form-control-lg" 
                    id="password"
                    v-model="formData.password"
                    required
                    placeholder="Create a strong password"
                    minlength="6"
                  >
                </div>
                
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password *</label>
                  <input 
                    type="password" 
                    class="form-control form-control-lg" 
                    id="confirmPassword"
                    v-model="confirmPassword"
                    required
                    placeholder="Re-enter your password"
                  >
                </div>
                
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg w-100 mb-3"
                  :disabled="loading"
                >
                  <span 
                    v-if="loading" 
                    class="spinner-border spinner-border-sm me-2"
                  ></span>
                  {{ loading ? 'Creating Account...' : 'Register' }}
                </button>
                
                <div class="text-center">
                  <p class="text-muted mb-0">
                    Already have an account? 
                    <router-link to="/login" class="text-decoration-none">
                      Login here
                    </router-link>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'
import { handleApiError, isValidEmail } from '@/utils/helpers'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const confirmPassword = ref('')
    
    const formData = ref({
      username: '',
      email: '',
      password: ''
    })
    
    const handleRegister = async () => {
      error.value = ''
      success.value = ''
      
      // Validation
      if (formData.value.password !== confirmPassword.value) {
        error.value = 'Passwords do not match'
        return
      }
      
      if (!isValidEmail(formData.value.email)) {
        error.value = 'Please enter a valid email address'
        return
      }
      
      loading.value = true
      
      try {
        await authAPI.register(formData.value)
        success.value = 'Account created successfully! Redirecting to login...'
        
        setTimeout(() => {
          router.push('/login')
        }, 2000)
      } catch (err) {
        error.value = handleApiError(err)
      } finally {
        loading.value = false
      }
    }
    
    return {
      formData,
      confirmPassword,
      loading,
      error,
      success,
      handleRegister
    }
  }
}
</script>