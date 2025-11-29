<template>
  <div class="container-fluid py-4">
    <Loader v-if="loading" />
    
    <div v-else>
      <div class="row mb-4">
        <div class="col">
          <h2>{{ lotData.lot.name }}</h2>
          <p class="text-muted">Parking spot details and management</p>
        </div>
        <div class="col-auto">
          <router-link to="/admin/lots" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-2"></i>
            Back
          </router-link>
        </div>
      </div>
      
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <h5>Parking Spots</h5>
          <div class="row g-3">
            <div 
              v-for="spot in lotData.spots" 
              :key="spot.id"
              class="col-md-2 col-sm-3 col-4"
            >
              <div 
                class="card text-center"
                :class="spot.status === 'A' ? 'border-success' : 'border-danger'"
              >
                <div class="card-body p-3">
                  <h6>#{{ spot.spot_number }}</h6>
                  <span 
                    :class="`badge ${spot.status === 'A' ? 'bg-success' : 'bg-danger'}`"
                  >
                    {{ spot.status === 'A' ? 'Available' : 'Occupied' }}
                  </span>
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminAPI } from '@/services/api'
import Loader from '@/components/Loader.vue'

export default {
  name: 'LotDetails',
  components: { Loader },
  setup() {
    const route = useRoute()
    const loading = ref(true)
    const lotData = ref({ lot: {}, spots: [] })
    
    const fetchLotDetails = async () => {
      try {
        const response = await adminAPI.getLotSpots(route.params.id)
        lotData.value = response.data
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(fetchLotDetails)
    
    return { loading, lotData }
  }
}
</script>