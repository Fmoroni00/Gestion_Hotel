import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("../views/Dashboard.vue"),
  },
  {
    path: "/recepcion",
    name: "recepcion",
    component: () => import("../views/Recepcion.vue"),
  },
  {
    path: "/limpieza",
    name: "limpieza",
    component: () => import("../views/Limpieza.vue"),
  },
  {
    path: "/huesped",
    name: "huesped",
    component: () => import("../views/Huesped.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
