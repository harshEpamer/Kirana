import { API } from '../config'

export const getProducts = (category, search) => {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (search)   params.set('search', search)
  return fetch(`${API.catalog}/catalog/products?${params}`).then(r => r.json())
}

export const getProduct = (id) =>
  fetch(`${API.catalog}/catalog/products/${id}`).then(r => r.json())

export const getCategories = () =>
  fetch(`${API.catalog}/catalog/categories`).then(r => r.json())
