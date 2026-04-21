import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', phone: '', address: '', password: '' })
  const [error, setError] = useState('')

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register(form.name, form.phone, form.address, form.password)
      navigate('/login')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-16 p-6 border rounded-lg shadow">
      <h1 className="text-2xl font-bold mb-6 text-green-700">Register</h1>
      {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input className="border p-2 rounded" placeholder="Full name"    value={form.name}     onChange={set('name')}     required />
        <input className="border p-2 rounded" type="tel" placeholder="Phone" value={form.phone} onChange={set('phone')}  required />
        <input className="border p-2 rounded" placeholder="Address"     value={form.address}  onChange={set('address')}  required />
        <input className="border p-2 rounded" type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
        <button className="bg-green-600 text-white py-2 rounded hover:bg-green-700">Register</button>
      </form>
      <p className="mt-4 text-sm text-center">
        Have an account? <Link to="/login" className="text-green-600 underline">Login</Link>
      </p>
    </div>
  )
}
