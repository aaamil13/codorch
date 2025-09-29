import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../pages/HomePage.vue'),
      },
      {
        path: '/projects',
        name: 'projects',
        component: () => import('../pages/ProjectsPage.vue'),
      },
      {
        path: '/project/:id',
        name: 'project-detail',
        component: () => import('../pages/ProjectDetailPage.vue'),
      },
      {
        path: '/project/:projectId/goals',
        name: 'project-goals',
        component: () => import('../pages/GoalsPage.vue'),
      },
      {
        path: '/project/:projectId/opportunities',
        name: 'project-opportunities',
        component: () => import('../pages/OpportunitiesPage.vue'),
      },
      {
        path: '/project/:projectId/research',
        name: 'project-research',
        component: () => import('../pages/ResearchPage.vue'),
      },
      {
        path: '/research/:sessionId',
        name: 'research-session',
        component: () => import('../pages/ResearchSessionPage.vue'),
      },
      {
        path: '/project/:projectId/architecture',
        name: 'project-architecture',
        component: () => import('../pages/ArchitecturePage.vue'),
      },
    ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('../pages/ErrorNotFound.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
