<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-5">
            <h2 class="mb-4">
              <i class="bi bi-person-circle me-2"></i>
              My Profile
            </h2>
            <div class="mb-3">
              <label class="form-label fw-bold">Username</label>
              <p class="form-control-plaintext">{{ username }}</p>
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">Role</label>
              <p class="form-control-plaintext">
                <span class="badge bg-primary">{{ role }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { getRole, getUserId } from '@/services/auth'

export default {
  name: 'Profile',
  setup() {
    const username = computed(() => localStorage.getItem('username') || 'User')
    const role = computed(() => getRole())
    
    return { username, role }
  }
}
</script>