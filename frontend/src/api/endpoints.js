import { apiClient } from "./client";

export const authApi = {
  login: (payload) => apiClient.post("/auth/login/", payload),
  me: () => apiClient.get("/auth/me/"),
};

export const dashboardApi = {
  getOverview: () => apiClient.get("/dashboard/"),
};

export const reportsApi = {
  getReports: (params) => apiClient.get("/reports/", { params }),
};

export const categoriesApi = {
  list: (params) => apiClient.get("/categories/", { params }),
  create: (payload) => apiClient.post("/categories/", payload),
  update: (id, payload) => apiClient.put(`/categories/${id}/`, payload),
  remove: (id) => apiClient.delete(`/categories/${id}/`),
};

export const productsApi = {
  list: (params) => apiClient.get("/products/", { params }),
  create: (payload) => apiClient.post("/products/", payload),
  update: (id, payload) => apiClient.put(`/products/${id}/`, payload),
  remove: (id) => apiClient.delete(`/products/${id}/`),
};

export const inventoryApi = {
  movements: (params) => apiClient.get("/inventory/movements/", { params }),
  adjust: (payload) => apiClient.post("/inventory/movements/adjust/", payload),
};

export const customersApi = {
  list: (params) => apiClient.get("/customers/", { params }),
  create: (payload) => apiClient.post("/customers/", payload),
  update: (id, payload) => apiClient.put(`/customers/${id}/`, payload),
  remove: (id) => apiClient.delete(`/customers/${id}/`),
};

export const salesApi = {
  list: (params) => apiClient.get("/sales/", { params }),
  create: (payload) => apiClient.post("/sales/", payload),
};

export const expensesApi = {
  list: (params) => apiClient.get("/expenses/", { params }),
  create: (payload) => apiClient.post("/expenses/", payload),
  update: (id, payload) => apiClient.put(`/expenses/${id}/`, payload),
  remove: (id) => apiClient.delete(`/expenses/${id}/`),
};

export const debtsApi = {
  list: (params) => apiClient.get("/debts/", { params }),
  collectPayment: (payload) => apiClient.post("/debts/collect_payment/", payload),
};
