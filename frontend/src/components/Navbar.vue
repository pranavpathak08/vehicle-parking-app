<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <router-link class="navbar-brand" :to="homeRoute">
        <i class="bi bi-car-front-fill me-2"></i>
        Parking Management
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <!-- Admin Menu -->
          <template v-if="isAdmin">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard">
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/lots">
                <i class="bi bi-building me-1"></i>
                Manage Lots
              </router-link>
            </li>
          </template>
          
          <!-- User Menu -->
          <template v-if="isUser">
            <li class="nav-item">
              <router-link class="nav-link" to="/user/dashboard">
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/lots">
                <i class="bi bi-p-square me-1"></i>
                Book Parking
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/reservations">
                <i class="bi bi-clock-history me-1"></i>
                My Bookings
              </router-link>
            </li>
          </template>
          
          <!-- Logout -->
          <li class="nav-item">
            <a 
              class="nav-link text-warning" 
              href="#" 
              @click.prevent="handleLogout"
            >
              <i class="bi bi-box-arrow-right me-1"></i>
              Logout
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { logout, isAdmin as checkIsAdmin, isUser as checkIsUser } from '@/services/auth'

export default {
  name: 'Navbar',
  setup() {
    const isAdmin = computed(() => checkIsAdmin())
    const isUser = computed(() => checkIsUser())
    
    const homeRoute = computed(() => {
      if (isAdmin.value) return '/admin/dashboard'
      if (isUser.value) return '/user/dashboard'
      return '/'
    })
    
    const handleLogout = () => {
      if (confirm('Are you sure you want to logout?')) {
        logout()
      }
    }
    
    return {
      isAdmin,
      isUser,
      homeRoute,
      handleLogout
    }
  }
}
</script>

<style scoped>
.nav-link {
  transition: all 0.3s ease;
}

.nav-link:hover {
  transform: translateY(-2px);
}

.navbar-brand {
  font-weight: 600;
  font-size: 1.25rem;
}
</style>