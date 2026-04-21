import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const listCustomers     = ()   => fetch(`${API.customers}/customers/`, { headers: h() }).then(r => r.json())
export const getCustomer       = (id) => fetch(`${API.customers}/customers/${id}`, { headers: h() }).then(r => r.json())
export const getPurchaseHistory = (id) => fetch(`${API.customers}/customers/${id}/history`, { headers: h() }).then(r => r.json())
