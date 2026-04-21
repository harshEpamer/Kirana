import { API, TOKEN_KEY } from '../config'

const h = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const listProducts       = ()      => fetch(`${API.inventory}/inventory/products`, { headers: h() }).then(r => r.json())
export const createProduct      = (data)  => fetch(`${API.inventory}/inventory/products`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
export const updateProduct      = (id, d) => fetch(`${API.inventory}/inventory/products/${id}`, { method: 'PUT', headers: h(), body: JSON.stringify(d) }).then(r => r.json())
export const deleteProduct      = (id)    => fetch(`${API.inventory}/inventory/products/${id}`, { method: 'DELETE', headers: h() })
export const adjustStock        = (data)  => fetch(`${API.inventory}/inventory/stock-adjust`, { method: 'POST', headers: h(), body: JSON.stringify(data) }).then(r => r.json())
export const patchStock         = (id, d) => fetch(`${API.inventory}/inventory/stock/${id}`, { method: 'PATCH', headers: h(), body: JSON.stringify(d) }).then(r => r.json())
export const restockProduct     = (id, qty) => patchStock(id, { adjustment_type: 'add', quantity: qty })
export const bulkImportProducts = (products) => fetch(`${API.inventory}/inventory/products/bulk`, { method: 'POST', headers: h(), body: JSON.stringify({ products }) }).then(r => r.json())
export const getStockLog        = ()      => fetch(`${API.inventory}/inventory/stock/log`, { headers: h() }).then(r => r.json())
