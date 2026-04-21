import { API, TOKEN_KEY } from '../config'

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
})

export const registerUser = (data) =>
  fetch(`${API.auth}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(r => r.json())

export const loginUser = (data) =>
  fetch(`${API.auth}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(r => r.json())

export const getMe = (token) =>
  fetch(`${API.auth}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then(r => r.json())
