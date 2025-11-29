import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, getRole } from '@/services/auth'

// Import views
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

// User views
import UserDashboard from '@/views/user/UserDashboard.vue'
import ParkingLots from '@/views/user/ParkingLots.vue'
import MyReservations from '@/views/user/MyReservations.vue'
import Profile from '@/views/user/Profile.vue'

// Admin views
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import ManageLots from '@/views/admin/ManageLots.vue'
import LotDetails from '@/views/admin/LotDetails.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresGuest: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  // User routes
  {
    path: '/user/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/user/lots',
    name: 'ParkingLots',
    component: ParkingLots,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/user/reservations',
    name: 'MyReservations',
    component: MyReservations,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/user/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true, role: 'user' }
  },
  // Admin routes
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/lots',
    name: 'ManageLots',
    component: ManageLots,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/lots/:id',
    name: 'LotDetails',
    component: LotDetails,
    meta: { requiresAuth: true, role: 'admin' }
  },
  // Catch all 404
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authRequired = to.meta.requiresAuth
  const guestOnly = to.meta.requiresGuest
  const requiredRole = to.meta.role
  const userAuthenticated = isAuthenticated()
  const userRole = getRole()

  // Guest only pages (login, register)
  if (guestOnly && userAuthenticated) {
    if (userRole === 'admin') {
      return next('/admin/dashboard')
    } else {
      return next('/user/dashboard')
    }
  }

  // Auth required pages
  if (authRequired && !userAuthenticated) {
    return next('/login')
  }

  // Role-based access
  if (authRequired && requiredRole && userRole !== requiredRole) {
    if (userRole === 'admin') {
      return next('/admin/dashboard')
    } else {
      return next('/user/dashboard')
    }
  }

  next()
})

export default router