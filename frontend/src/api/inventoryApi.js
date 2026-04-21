import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const listProducts   = ()      => fetch(`${API.inventory}/inventory/products`, { headers: h() }).then(r => r.json())
export const createProduct  = (data)  => fetch(`${API.inventory}/inventory/products`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
export const updateProduct  = (id, d) => fetch(`${API.inventory}/inventory/products/${id}`, { method: 'PUT', headers: h(), body: JSON.stringify(d) }).then(r => r.json())
export const deleteProduct  = (id)    => fetch(`${API.inventory}/inventory/products/${id}`, { method: 'DELETE', headers: h() })
export const adjustStock    = (data)  => fetch(`${API.inventory}/inventory/stock-adjust`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
export const getLowStock    = ()      => fetch(`${API.inventory}/inventory/low-stock`, { headers: h() }).then(r => r.json())
export const bulkInsert     = (data)  => fetch(`${API.inventory}/inventory/products/bulk`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
export const getReorderList = ()      => fetch(`${API.inventory}/inventory/reorder`, { headers: h() }).then(r => r.json())
