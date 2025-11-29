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
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="card-title mb-0">{{ lot.name }}</h5>
              <span class="badge bg-primary">₹{{ lot.price_per_hour }}/hr</span>
            </div>
            
            <p class="text-muted mb-2">
              <i class="bi bi-geo-alt me-1"></i>
              {{ lot.address || 'No address' }}
            </p>
            <p class="text-muted mb-3">
              <i class="bi bi-mailbox me-1"></i>
              {{ lot.pincode || 'No pincode' }}
            </p>
            
            <div class="row g-2 mb-3">
              <div class="col-4">
                <small class="text-muted d-block">Available</small>
                <div class="fw-bold text-success">{{ lot.available }}</div>
              </div>
              <div class="col-4">
                <small class="text-muted d-block">Occupied</small>
                <div class="fw-bold text-danger">{{ lot.occupied }}</div>
              </div>
              <div class="col-4">
                <small class="text-muted d-block">Total</small>
                <div class="fw-bold">{{ lot.number_of_spots }}</div>
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
                class="btn btn-outline-info btn-sm"
                @click="openEditModal(lot)"
              >
                <i class="bi bi-pencil me-1"></i>
                Edit
              </button>
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
                <label class="form-label">Price per Hour (₹) *</label>
                <input type="number" class="form-control" v-model="newLot.price_per_hour" required min="0" step="0.01">
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots *</label>
                <input type="number" class="form-control" v-model="newLot.number_of_spots" required min="1">
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="creating">
                <span v-if="creating" class="spinner-border spinner-border-sm me-2"></span>
                {{ creating ? 'Creating...' : 'Create Lot' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Lot Modal -->
    <div class="modal fade" id="editLotModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Parking Lot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleUpdate">
              <div class="mb-3">
                <label class="form-label">Name *</label>
                <input type="text" class="form-control" v-model="editLot.name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <input type="text" class="form-control" v-model="editLot.address">
              </div>
              <div class="mb-3">
                <label class="form-label">Pincode</label>
                <input type="text" class="form-control" v-model="editLot.pincode">
              </div>
              <div class="mb-3">
                <label class="form-label">Price per Hour (₹) *</label>
                <input type="number" class="form-control" v-model="editLot.price_per_hour" required min="0" step="0.01">
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="editLot.number_of_spots" 
                  required 
                  min="0"
                  :min="editLot.current_spots"
                >
                <div class="form-text">
                  Current: {{ editLot.current_spots }} spots ({{ editLot.occupied }} occupied)
                  <br>
                  <span v-if="editLot.number_of_spots < editLot.current_spots" class="text-warning">
                    <i class="bi bi-exclamation-triangle me-1"></i>
                    Reducing spots will remove the last {{ editLot.current_spots - editLot.number_of_spots }} spot(s) if they're available.
                  </span>
                  <span v-else-if="editLot.number_of_spots > editLot.current_spots" class="text-success">
                    <i class="bi bi-plus-circle me-1"></i>
                    Will add {{ editLot.number_of_spots - editLot.current_spots }} new spot(s).
                  </span>
                </div>
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="updating">
                <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                {{ updating ? 'Updating...' : 'Update Lot' }}
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
    const updating = ref(false)
    const lots = ref([])
    
    const newLot = ref({
      name: '',
      address: '',
      pincode: '',
      price_per_hour: 50,
      number_of_spots: 10
    })

    const editLot = ref({
      id: null,
      name: '',
      address: '',
      pincode: '',
      price_per_hour: 50,
      number_of_spots: 10,
      current_spots: 10,
      occupied: 0
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
        newLot.value = { 
          name: '', 
          address: '', 
          pincode: '', 
          price_per_hour: 50, 
          number_of_spots: 10 
        }
        await fetchLots()
      } catch (error) {
        alert(handleApiError(error))
      } finally {
        creating.value = false
      }
    }

    const openEditModal = async (lot) => {
      try {
        // Fetch fresh lot data
        const response = await adminAPI.getLot(lot.id)
        const lotData = response.data
        
        editLot.value = {
          id: lotData.id,
          name: lotData.name,
          address: lotData.address || '',
          pincode: lotData.pincode || '',
          price_per_hour: lotData.price_per_hour,
          number_of_spots: lotData.number_of_spots,
          current_spots: lotData.number_of_spots,
          occupied: lotData.occupied
        }
        
        // Show modal
        const modalElement = document.getElementById('editLotModal')
        const modal = new window.bootstrap.Modal(modalElement)
        modal.show()
      } catch (error) {
        alert(handleApiError(error))
      }
    }

    const handleUpdate = async () => {
      // Validation: Cannot reduce spots below occupied count
      if (editLot.value.number_of_spots < editLot.value.occupied) {
        alert(`Cannot reduce spots to ${editLot.value.number_of_spots}. There are ${editLot.value.occupied} occupied spots.`)
        return
      }

      updating.value = true
      try {
        await adminAPI.updateLot(editLot.value.id, {
          name: editLot.value.name,
          address: editLot.value.address,
          pincode: editLot.value.pincode,
          price_per_hour: editLot.value.price_per_hour,
          number_of_spots: editLot.value.number_of_spots
        })
        
        alert('Parking lot updated successfully!')
        const modal = window.bootstrap.Modal.getInstance(document.getElementById('editLotModal'))
        modal.hide()
        await fetchLots()
      } catch (error) {
        alert(handleApiError(error))
      } finally {
        updating.value = false
      }
    }
    
    const handleDelete = async (id) => {
      if (!confirm('Delete this parking lot? This action cannot be undone.')) return
      
      try {
        await adminAPI.deleteLot(id)
        alert('Parking lot deleted successfully!')
        await fetchLots()
      } catch (error) {
        alert(handleApiError(error))
      }
    }
    
    onMounted(fetchLots)
    
    return { 
      loading, 
      creating, 
      updating,
      lots, 
      newLot,
      editLot,
      handleCreate,
      openEditModal,
      handleUpdate,
      handleDelete 
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

.form-text {
  font-size: 0.875rem;
  line-height: 1.4;
}
</style>