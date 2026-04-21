import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const placeOrder = (checkoutData, token) =>
  fetch(`${API.orders}/orders/checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(checkoutData),
  }).then(r => {
    if (!r.ok) return r.json().then(e => Promise.reject(e))
    return r.json()
  })

// Backward-compatible alias for CartPage
export const checkout = (data) =>
  fetch(`${API.orders}/orders/checkout`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
