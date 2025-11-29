<template>
  <div id="app">
    <Navbar v-if="!isAuthPage" />
    <main class="flex-grow-1">
      <router-view />
    </main>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  },
  setup() {
    const route = useRoute()
    
    const isAuthPage = computed(() => {
      return ['Login', 'Register', 'Home'].includes(route.name)
    })

    return {
      isAuthPage
    }
  }
}
</script>

<style>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}
</style>