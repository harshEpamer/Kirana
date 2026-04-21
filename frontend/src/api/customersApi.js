import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const getAllCustomers = (token) =>
  fetch(`${API.customers}/customers/`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(r => r.json())

export const getCustomerHistory = (userId, token) =>
  fetch(`${API.customers}/customers/${userId}/history`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(r => r.json())

// Backward-compatible aliases
export const listCustomers      = () => fetch(`${API.customers}/customers/`, { headers: h() }).then(r => r.json())
export const getPurchaseHistory = (id) => fetch(`${API.customers}/customers/${id}/history`, { headers: h() }).then(r => r.json())
