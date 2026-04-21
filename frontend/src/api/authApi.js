import { API, TOKEN_KEY } from '../config'

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const login = (phone, password) =>
  fetch(`${API.auth}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, password }),
  }).then(r => r.json())

export const register = (name, phone, address, password) =>
  fetch(`${API.auth}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, phone, address, password }),
  }).then(r => r.json())
