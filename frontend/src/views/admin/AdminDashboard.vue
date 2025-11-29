<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2>
          <i class="bi bi-speedometer2 me-2"></i>
          Admin Dashboard
        </h2>
        <p class="text-muted">System overview and statistics</p>
      </div>
    </div>
    
    <Loader v-if="loading" />
    
    <div v-else>
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <p class="text-muted mb-1">Total Lots</p>
                  <h3>{{ stats.total_lots }}</h3>
                </div>
                <i class="bi bi-building display-4 text-primary opacity-25"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <p class="text-muted mb-1">Total Spots</p>
                  <h3>{{ stats.total_spots }}</h3>
                </div>
                <i class="bi bi-p-square display-4 text-success opacity-25"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <p class="text-muted mb-1">Occupied</p>
                  <h3>{{ stats.occupied_spots }}</h3>
                  <small :class="getOccupancyClass(stats.occupancy_rate)">
                    {{ stats.occupancy_rate }}% occupancy
                  </small>
                </div>
                <i class="bi bi-car-front display-4 text-warning opacity-25"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <p class="text-muted mb-1">Month Revenue</p>
                  <h3>{{ formatCurrency(stats.month_revenue) }}</h3>
                </div>
                <i class="bi bi-currency-rupee display-4 text-info opacity-25"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row g-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">Quick Actions</h5>
              <div class="d-grid gap-2">
                <router-link to="/admin/lots" class="btn btn-primary">
                  <i class="bi bi-plus-circle me-2"></i>
                  Manage Parking Lots
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">System Info</h5>
              <ul class="list-unstyled mb-0">
                <li><strong>Active Reservations:</strong> {{ stats.active_reservations }}</li>
                <li><strong>Total Users:</strong> {{ stats.total_users }}</li>
                <li><strong>Today's Revenue:</strong> {{ formatCurrency(stats.today_revenue) }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/services/api'
import { formatCurrency, getOccupancyClass } from '@/utils/helpers'
import Loader from '@/components/Loader.vue'

export default {
  name: 'AdminDashboard',
  components: { Loader },
  setup() {
    const loading = ref(true)
    const stats = ref({})
    
    const fetchStats = async () => {
      try {
        const response = await adminAPI.getDashboardStats()
        stats.value = response.data
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(fetchStats)
    
    return { loading, stats, formatCurrency, getOccupancyClass }
  }
}
</script>