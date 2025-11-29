// Format date and time
export function formatDateTime(dateString) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // Format date only
  export function formatDate(dateString) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
  
  // Format time only
  export function formatTime(dateString) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // Calculate duration between two dates
  export function calculateDuration(startDate, endDate) {
    if (!startDate) return 'N/A'
    
    const start = new Date(startDate)
    const end = endDate ? new Date(endDate) : new Date()
    
    const diffMs = end - start
    const diffMins = Math.floor(diffMs / 60000)
    const hours = Math.floor(diffMins / 60)
    const minutes = diffMins % 60
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }
  
  // Format currency
  export function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '₹0.00'
    return `₹${parseFloat(amount).toFixed(2)}`
  }
  
  // Get status badge class
  export function getStatusClass(status) {
    const statusMap = {
      'active': 'bg-success',
      'completed': 'bg-secondary',
      'cancelled': 'bg-danger',
      'pending': 'bg-warning',
      'processing': 'bg-info',
      'done': 'bg-success',
      'failed': 'bg-danger'
    }
    return statusMap[status?.toLowerCase()] || 'bg-secondary'
  }
  
  // Get occupancy color
  export function getOccupancyClass(rate) {
    if (rate >= 90) return 'text-danger'
    if (rate >= 70) return 'text-warning'
    return 'text-success'
  }
  
  // Handle API errors
  export function handleApiError(error) {
    if (error.response) {
      return error.response.data.msg || error.response.data.message || 'An error occurred'
    } else if (error.request) {
      return 'No response from server. Please check your connection.'
    }
    return error.message || 'An unexpected error occurred'
  }
  
  // Download blob as file
  export function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }
  
  // Validate email
  export function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  }