<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2 class="mb-0">
          <i class="bi bi-speedometer2 me-2"></i>
          Dashboard
        </h2>
        <p class="text-muted">Welcome back! Here's your parking overview</p>
      </div>
    </div>
    
    <Loader v-if="loading" message="Loading dashboard..." />
    
    <div v-else>
      <!-- Active Reservation Alert -->
      <div v-if="activeReservation" class="alert alert-success shadow-sm mb-4" role="alert">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h5 class="alert-heading mb-2">
              <i class="bi bi-check-circle-fill me-2"></i>
              Active Parking Session
            </h5>
            <p class="mb-2">
              <strong>Location:</strong> {{ activeReservation.lot_name || 'N/A' }}<br>
              <strong>Spot:</strong> #{{ activeReservation.spot_number }}<br>
              <strong>Started:</strong> {{ formatDateTime(activeReservation.parking_timestamp) }}
            </p>
          </div>
          <button 
            class="btn btn-warning"
            @click="handleLeave"
            :disabled="leaving"
          >
            <span v-if="leaving" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-door-open me-2"></i>
            {{ leaving ? 'Processing...' : 'Leave Spot' }}
          </button>
        </div>
      </div>
      
      <!-- Statistics Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted mb-1">Total Bookings</p>
                  <h3 class="mb-0">{{ stats.totalBookings }}</h3>
                </div>
                <div class="bg-primary bg-opacity-10 p-3 rounded">
                  <i class="bi bi-calendar-check text-primary fs-3"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted mb-1">Active Sessions</p>
                  <h3 class="mb-0">{{ stats.activeBookings }}</h3>
                </div>
                <div class="bg-success bg-opacity-10 p-3 rounded">
                  <i class="bi bi-hourglass-split text-success fs-3"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted mb-1">Total Spent</p>
                  <h3 class="mb-0">{{ formatCurrency(stats.totalSpent) }}</h3>
                </div>
                <div class="bg-warning bg-opacity-10 p-3 rounded">
                  <i class="bi bi-currency-rupee text-warning fs-3"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted mb-1">Completed</p>
                  <h3 class="mb-0">{{ stats.completedBookings }}</h3>
                </div>
                <div class="bg-info bg-opacity-10 p-3 rounded">
                  <i class="bi bi-check2-all text-info fs-3"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-lightning-charge-fill text-warning me-2"></i>
                Quick Actions
              </h5>
              <div class="d-grid gap-2">
                <router-link 
                  to="/user/lots" 
                  class="btn btn-primary btn-lg"
                  :class="{ disabled: activeReservation }"
                >
                  <i class="bi bi-plus-circle me-2"></i>
                  Book New Parking Spot
                </router-link>
                <router-link 
                  to="/user/reservations" 
                  class="btn btn-outline-primary btn-lg"
                >
                  <i class="bi bi-clock-history me-2"></i>
                  View All Reservations
                </router-link>
                <button 
                  class="btn btn-outline-success btn-lg"
                  @click="handleExport"
                  :disabled="exporting"
                >
                  <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-download me-2"></i>
                  {{ exporting ? 'Exporting...' : 'Export History (CSV)' }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-info-circle-fill text-info me-2"></i>
                Recent Activity
              </h5>
              <div v-if="recentReservations.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-inbox display-4 mb-3 d-block"></i>
                <p>No recent activity</p>
              </div>
              <div v-else class="list-group list-group-flush">
                <div 
                  v-for="reservation in recentReservations" 
                  :key="reservation.id"
                  class="list-group-item px-0"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-1">{{ reservation.lot_name }}</h6>
                      <small class="text-muted">
                        Spot #{{ reservation.spot_number }} • 
                        {{ formatDate(reservation.parking_timestamp) }}
                      </small>
                    </div>
                    <span :class="`badge ${getStatusClass(reservation.status)}`">
                      {{ reservation.status }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { userAPI } from '@/services/api'
import { formatDateTime, formatDate, formatCurrency, getStatusClass, handleApiError } from '@/utils/helpers'
import Loader from '@/components/Loader.vue'

export default {
  name: 'UserDashboard',
  components: { Loader },
  setup() {
    const loading = ref(true)
    const leaving = ref(false)
    const exporting = ref(false)
    const reservations = ref([])
    
    const activeReservation = computed(() => {
      return reservations.value.find(r => r.status === 'active')
    })
    
    const stats = computed(() => {
      const total = reservations.value.length
      const active = reservations.value.filter(r => r.status === 'active').length
      const completed = reservations.value.filter(r => r.status === 'completed').length
      const totalSpent = reservations.value
        .filter(r => r.parking_cost)
        .reduce((sum, r) => sum + r.parking_cost, 0)
      
      return {
        totalBookings: total,
        activeBookings: active,
        completedBookings: completed,
        totalSpent
      }
    })
    
    const recentReservations = computed(() => {
      return reservations.value.slice(0, 5)
    })
    
    const fetchReservations = async () => {
      try {
        const response = await userAPI.getMyReservations()
        reservations.value = response.data
      } catch (error) {
        console.error('Error fetching reservations:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleLeave = async () => {
      if (!confirm('Are you sure you want to leave this parking spot?')) return
      
      leaving.value = true
      try {
        const response = await userAPI.leaveSpot(activeReservation.value.id)
        alert(`Parking session ended. Total cost: ${formatCurrency(response.data.parking_cost)}`)
        await fetchReservations()
      } catch (error) {
        alert(handleApiError(error))
      } finally {
        leaving.value = false
      }
    }
    
    const handleExport = async () => {
      exporting.value = true
      try {
        await userAPI.triggerExport()
        alert('Export requested! You will receive an email with your parking history CSV file shortly.')
      } catch (error) {
        alert(handleApiError(error))
      } finally {
        exporting.value = false
      }
    }
    
    onMounted(() => {
      fetchReservations()
    })
    
    return {
      loading,
      leaving,
      exporting,
      activeReservation,
      stats,
      recentReservations,
      handleLeave,
      handleExport,
      formatDateTime,
      formatDate,
      formatCurrency,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}
</style>