<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2>
          <i class="bi bi-clock-history me-2"></i>
          My Reservations
        </h2>
        <p class="text-muted">View your parking history</p>
      </div>
    </div>
    
    <Loader v-if="loading" />
    
    <div v-else-if="reservations.length === 0" class="text-center py-5">
      <i class="bi bi-inbox display-1 text-muted mb-3"></i>
      <h4>No reservations found</h4>
      <router-link to="/user/lots" class="btn btn-primary mt-3">
        Book Your First Spot
      </router-link>
    </div>
    
    <div v-else class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Parking Lot</th>
                <th>Spot</th>
                <th>Check-in</th>
                <th>Check-out</th>
                <th>Duration</th>
                <th>Cost</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reservation in reservations" :key="reservation.id">
                <td>{{ reservation.id }}</td>
                <td>{{ reservation.lot_name }}</td>
                <td>#{{ reservation.spot_number }}</td>
                <td>{{ formatDateTime(reservation.parking_timestamp) }}</td>
                <td>{{ formatDateTime(reservation.leaving_timestamp) }}</td>
                <td>{{ calculateDuration(reservation.parking_timestamp, reservation.leaving_timestamp) }}</td>
                <td>{{ formatCurrency(reservation.parking_cost) }}</td>
                <td>
                  <span :class="`badge ${getStatusClass(reservation.status)}`">
                    {{ reservation.status }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="reservation.status === 'active'"
                    class="btn btn-sm btn-warning"
                    @click="handleLeave(reservation.id)"
                  >
                    <i class="bi bi-door-open"></i>
                    Leave
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { userAPI } from '@/services/api'
import { formatDateTime, calculateDuration, formatCurrency, getStatusClass, handleApiError } from '@/utils/helpers'
import Loader from '@/components/Loader.vue'

export default {
  name: 'MyReservations',
  components: { Loader },
  setup() {
    const loading = ref(true)
    const reservations = ref([])
    
    const fetchReservations = async () => {
      try {
        const response = await userAPI.getMyReservations()
        reservations.value = response.data
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    const handleLeave = async (id) => {
      if (!confirm('Leave this parking spot?')) return
      try {
        await userAPI.leaveSpot(id)
        alert('Parking session ended successfully!')
        await fetchReservations()
      } catch (error) {
        alert(handleApiError(error))
      }
    }
    
    onMounted(fetchReservations)
    
    return { loading, reservations, handleLeave, formatDateTime, calculateDuration, formatCurrency, getStatusClass }
  }
}
</script>