<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-lg-6 mb-5 mb-lg-0">
          <h1 class="display-3 fw-bold mb-4">
            <i class="bi bi-car-front-fill text-primary"></i>
            Vehicle Parking Management
          </h1>
          <p class="lead text-muted mb-4">
            Find, book, and manage parking spaces effortlessly. Say goodbye to parking hassles with our smart reservation system.
          </p>
          <div class="d-flex gap-3">
            <router-link to="/register" class="btn btn-primary btn-lg">
              <i class="bi bi-person-plus me-2"></i>
              Get Started
            </router-link>
            <router-link to="/login" class="btn btn-outline-primary btn-lg">
              <i class="bi bi-box-arrow-in-right me-2"></i>
              Login
            </router-link>
          </div>
        </div>
        
        <div class="col-lg-6">
          <div class="row g-4">
            <div class="col-sm-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body text-center">
                  <div class="mb-3">
                    <i class="bi bi-search display-4 text-primary"></i>
                  </div>
                  <h5 class="card-title">Find Parking</h5>
                  <p class="card-text text-muted">
                    Search and discover available parking spots near you
                  </p>
                </div>
              </div>
            </div>
            
            <div class="col-sm-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body text-center">
                  <div class="mb-3">
                    <i class="bi bi-calendar-check display-4 text-success"></i>
                  </div>
                  <h5 class="card-title">Book Instantly</h5>
                  <p class="card-text text-muted">
                    Reserve your spot with just one click
                  </p>
                </div>
              </div>
            </div>
            
            <div class="col-sm-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body text-center">
                  <div class="mb-3">
                    <i class="bi bi-shield-check display-4 text-info"></i>
                  </div>
                  <h5 class="card-title">Secure Payment</h5>
                  <p class="card-text text-muted">
                    Safe and transparent pricing with no hidden fees
                  </p>
                </div>
              </div>
            </div>
            
            <div class="col-sm-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body text-center">
                  <div class="mb-3">
                    <i class="bi bi-clock-history display-4 text-warning"></i>
                  </div>
                  <h5 class="card-title">Track History</h5>
                  <p class="card-text text-muted">
                    View and export your complete parking history
                  </p>
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
export default {
  name: 'Home'
}
</script>

<style scoped>
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
</style>