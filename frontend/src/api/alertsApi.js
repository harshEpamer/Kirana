import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const getLowStockAlerts  = ()   => fetch(`${API.alerts}/alerts/low-stock`, { headers: h() }).then(r => r.json())
export const getDashboardStats  = ()   => fetch(`${API.alerts}/alerts/dashboard`, { headers: h() }).then(r => r.json())
export const checkProduct       = (id) => fetch(`${API.alerts}/alerts/check/${id}`, { headers: h() }).then(r => r.json())
