import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import AuthLayout from '@/layouts/AuthLayout.vue'
import MainLayout from '@/layouts/MainLayout.vue'

// Auth Pages
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'

// Main Pages
import DashboardPage from '@/pages/DashboardPage.vue'
import ComplaintsListPage from '@/pages/ComplaintsListPage.vue'
import ComplaintDetailPage from '@/pages/ComplaintDetailPage.vue'
import CreateComplaintPage from '@/pages/CreateComplaintPage.vue'
import MyComplaintsPage from '@/pages/MyComplaintsPage.vue'
import LeaderboardPage from '@/pages/LeaderboardPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'
import NotificationsPage from '@/pages/NotificationsPage.vue'
import AdminPanelPage from '@/pages/AdminPanelPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'login',
        component: LoginPage,
        meta: { guest: true }
      },
      {
        path: 'register',
        name: 'register',
        component: RegisterPage,
        meta: { guest: true }
      }
    ]
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardPage
      },
      {
        path: 'complaints',
        name: 'complaints',
        component: ComplaintsListPage
      },
      {
        path: 'complaints/new',
        name: 'create-complaint',
        component: CreateComplaintPage
      },
      {
        path: 'complaints/:id',
        name: 'complaint-detail',
        component: ComplaintDetailPage,
        props: true
      },
      {
        path: 'my-complaints',
        name: 'my-complaints',
        component: MyComplaintsPage
      },
      {
        path: 'leaderboard',
        name: 'leaderboard',
        component: LeaderboardPage
      },
      {
        path: 'profile',
        name: 'profile',
        component: ProfilePage
      },
      {
        path: 'notifications',
        name: 'notifications',
        component: NotificationsPage
      },
      {
        path: 'admin',
        name: 'admin',
        component: AdminPanelPage,
        meta: { requiresSecretary: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else if (to.meta.requiresSecretary && !authStore.isSecretary) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
