<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2>
          <i class="bi bi-building me-2"></i>
          Manage Parking Lots
        </h2>
      </div>
      <div class="col-auto">
        <button 
          class="btn btn-primary"
          data-bs-toggle="modal"
          data-bs-target="#createLotModal"
        >
          <i class="bi bi-plus-circle me-2"></i>
          Create New Lot
        </button>
      </div>
    </div>
    
    <Loader v-if="loading" />
    
    <div v-else-if="lots.length === 0" class="text-center py-5">
      <i class="bi bi-inbox display-1 text-muted mb-3"></i>
      <h4>No parking lots</h4>
      <button class="btn btn-primary mt-3" data-bs-toggle="modal" data-bs-target="#createLotModal">
        Create First Lot
      </button>
    </div>
    
    <div v-else class="row g-4">
      <div v-for="lot in lots" :key="lot.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title">{{ lot.name }}</h5>
            <p class="text-muted mb-2">{{ lot.address }}</p>
            
            <div class="row g-2 mb-3">
              <div class="col-6">
                <small class="text-muted">Available</small>
                <div class="fw-bold text-success">{{ lot.available }}</div>
              </div>
              <div class="col-6">
                <small class="text-muted">Occupied</small>
                <div class="fw-bold text-danger">{{ lot.occupied }}</div>
              </div>
            </div>
            
            <div class="d-grid gap-2">
              <router-link 
                :to="`/admin/lots/${lot.id}`"
                class="btn btn-outline-primary btn-sm"
              >
                <i class="bi bi-eye me-1"></i>
                View Details
              </router-link>
              <button 
                class="btn btn-outline-danger btn-sm"
                @click="handleDelete(lot.id)"
              >
                <i class="bi bi-trash me-1"></i>
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create Lot Modal -->
    <div class="modal fade" id="createLotModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Parking Lot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleCreate">
              <div class="mb-3">
                <label class="form-label">Name *</label>
                <input type="text" class="form-control" v-model="newLot.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <input type="text" class="form-control" v-model="newLot.address">
              </div>
              <div class="mb-3">
                <label class="form-label">Pincode</label>
                <input type="text" class="form-control" v-model="newLot.pincode">
              </div>
              <div class="mb-3">
                <label class="form-label">Price per Hour *</label>
                <input type="number" class="form-control" v-model="newLot.price_per_hour" required min="0">
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots *</label>
                <input type="number" class="form-control" v-model="newLot.number_of_spots" required min="1">
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="creating">
                {{ creating ? 'Creating...' : 'Create Lot' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import { handleApiError } from '@/utils/helpers'
import Loader from '@/components/Loader.vue'

export default {
  name: 'ManageLots',
  components: { Loader },
  setup() {
    const loading = ref(true)
    const creating = ref(false)
    const lots = ref([])
    const newLot = ref({
      name: '',
      address: '',
      pincode: '',
      price_per_hour: 50,
      number_of_spots: 10
    })
    
    const fetchLots = async () => {
      try {
        const response = await adminAPI.getLots()
        lots.value = response.data
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    const handleCreate = async () => {
      creating.value = true
      try {
        await adminAPI.createLot(newLot.value)
        alert('Parking lot created successfully!')
        const modal = window.bootstrap.Modal.getInstance(document.getElementById('createLotModal'))
        modal.hide()
        newLot.value = { name: '', address: '', pincode: '', price_per_hour: 50, number_of_spots: 10 }
        await fetchLots()
      } catch (error) {
        alert(handleApiError(error))
      } finally {
        creating.value = false
      }
    }
    
    const handleDelete = async (id) => {
      if (!confirm('Delete this parking lot?')) return
      try {
        await adminAPI.deleteLot(id)
        alert('Parking lot deleted successfully!')
        await fetchLots()
      } catch (error) {
        alert(handleApiError(error))
      }
    }
    
    onMounted(fetchLots)
    
    return { loading, creating, lots, newLot, handleCreate, handleDelete }
  }
}
</script>
