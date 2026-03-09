import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import EstimatePage from '../views/EstimatePage.vue'
import PreBookingPage from '../views/PreBookingPage.vue'
import QuestionsPage from '../views/QuestionsPage.vue'
import ContactPage from '../views/ContactPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/estimate',
    name: 'Estimate',
    component: EstimatePage
  },
  {
    path: '/pre-booking',
    name: 'PreBooking',
    component: PreBookingPage
  },
  {
    path: '/questions',
    name: 'Questions',
    component: QuestionsPage
  },
  {
    path: '/contact',
    name: 'Contact',
    component: ContactPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router