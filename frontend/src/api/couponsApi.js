import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const listCoupons    = ()     => fetch(`${API.coupons}/coupons/`, { headers: h() }).then(r => r.json())
export const validateCoupon = (data) => fetch(`${API.coupons}/coupons/validate`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
export const createCoupon   = (data) => fetch(`${API.coupons}/coupons/`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
