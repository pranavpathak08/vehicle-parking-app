<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-5">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <i class="bi bi-car-front-fill text-primary display-3"></i>
                <h2 class="mt-3">Welcome Back</h2>
                <p class="text-muted">Login to your account</p>
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
              
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    id="username"
                    v-model="credentials.username"
                    required
                    placeholder="Enter your username"
                  >
                </div>
                
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input 
                    type="password" 
                    class="form-control form-control-lg" 
                    id="password"
                    v-model="credentials.password"
                    required
                    placeholder="Enter your password"
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
                  {{ loading ? 'Logging in...' : 'Login' }}
                </button>
                
                <div class="text-center">
                  <p class="text-muted mb-0">
                    Don't have an account? 
                    <router-link to="/register" class="text-decoration-none">
                      Register here
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
import { setToken, setUserData } from '@/services/auth'
import { handleApiError } from '@/utils/helpers'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    const credentials = ref({
      username: '',
      password: ''
    })
    
    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await authAPI.login(credentials.value)
        const { access_token, role, user_id } = response.data
        
        setToken(access_token)
        setUserData(role, user_id)
        
        // Redirect based on role
        if (role === 'admin') {
          router.push('/admin/dashboard')
        } else {
          router.push('/user/dashboard')
        }
      } catch (err) {
        error.value = handleApiError(err)
      } finally {
        loading.value = false
      }
    }
    
    return {
      credentials,
      loading,
      error,
      handleLogin
    }
  }
}
</script>