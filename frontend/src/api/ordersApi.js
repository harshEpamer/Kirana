import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const checkout = (data) =>
  fetch(`${API.orders}/orders/`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
