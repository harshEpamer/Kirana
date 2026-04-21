import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const listSales = () => fetch(`${API.sales}/sales/`, { headers: h() }).then(r => r.json())
export const getSale   = (id) => fetch(`${API.sales}/sales/${id}`, { headers: h() }).then(r => r.json())
export const createSale = (data) =>
  fetch(`${API.sales}/sales/`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
