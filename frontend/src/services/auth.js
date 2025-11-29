// Authentication helper functions

export function setToken(token) {
    localStorage.setItem('access_token', token)
  }
  
  export function getToken() {
    return localStorage.getItem('access_token')
  }
  
  export function removeToken() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_id')
  }
  
  export function setUserData(role, userId) {
    localStorage.setItem('user_role', role)
    localStorage.setItem('user_id', userId)
  }
  
  export function getRole() {
    return localStorage.getItem('user_role')
  }
  
  export function getUserId() {
    return localStorage.getItem('user_id')
  }
  
  export function isAuthenticated() {
    return !!getToken()
  }
  
  export function isAdmin() {
    return getRole() === 'admin'
  }
  
  export function isUser() {
    return getRole() === 'user'
  }
  
  export function logout() {
    removeToken()
    window.location.href = '/login'
  }