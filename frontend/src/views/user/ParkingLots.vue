<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2>
          <i class="bi bi-p-square me-2"></i>
          Available Parking Lots
        </h2>
        <p class="text-muted">Find and book your parking spot</p>
      </div>
    </div>
    
    <Loader v-if="loading" />
    
    <div v-else-if="lots.length === 0" class="text-center py-5">
      <i class="bi bi-inbox display-1 text-muted mb-3"></i>
      <h4>No parking lots available</h4>
    </div>
    
    <div v-else class="row g-4">
      <div v-for="lot in lots" :key="lot.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="card-title mb-0">{{ lot.name }}</h5>
              <span class="badge bg-primary">
                {{ formatCurrency(lot.price_per_hour) }}/hr
              </span>
            </div>
            
            <p class="text-muted mb-2">
              <i class="bi bi-geo-alt me-1"></i>
              {{ lot.address || 'N/A' }}
            </p>
            
            <div class="row g-2 mb-3">
              <div class="col-6">
                <div class="bg-light p-2 rounded text-center">
                  <small class="text-muted d-block">Available</small>
                  <strong class="text-success">{{ lot.available_spots }}</strong>
                </div>
              </div>
              <div class="col-6">
                <div class="bg-light p-2 rounded text-center">
                  <small class="text-muted d-block">Total</small>
                  <strong>{{ lot.total_spots }}</strong>
                </div>
              </div>
            </div>
            
            <button 
              class="btn btn-primary w-100"
              @click="handleBook(lot.id)"
              :disabled="lot.available_spots === 0 || booking"
            >
              <i class="bi bi-bookmark-plus me-2"></i>
              {{ lot.available_spots === 0 ? 'Full' : 'Book Now' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI } from '@/services/api'
import { formatCurrency, handleApiError } from '@/utils/helpers'
import Loader from '@/components/Loader.vue'

export default {
  name: 'ParkingLots',
  components: { Loader },
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const booking = ref(false)
    const lots = ref([])
    
    const fetchLots = async () => {
      try {
        const response = await userAPI.getLots()
        lots.value = response.data
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    const handleBook = async (lotId) => {
      booking.value = true
      try {
        await userAPI.bookSpot(lotId)
        alert('Parking spot booked successfully!')
        router.push('/user/dashboard')
      } catch (error) {
        alert(handleApiError(error))
        await fetchLots()
      } finally {
        booking.value = false
      }
    }
    
    onMounted(fetchLots)
    
    return { loading, booking, lots, handleBook, formatCurrency }
  }
}
</script>