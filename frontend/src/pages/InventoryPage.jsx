import { useState, useEffect } from 'react'
import { listProducts, createProduct, updateProduct, deleteProduct, adjustStock } from '../api/inventoryApi'

const EMPTY = { name: '', category: '', price: '', stock_qty: '', reorder_threshold: '10', image_url: '' }

export default function InventoryPage() {
  const [products, setProducts] = useState([])
  const [form,     setForm]     = useState(EMPTY)
  const [editing,  setEditing]  = useState(null)
  const [adjForm,  setAdjForm]  = useState({ product_id: '', adjustment_type: 'add', quantity: '' })
  const [msg,      setMsg]      = useState('')

  const load = () => listProducts().then(setProducts)
  useEffect(() => { load() }, [])

  const set = (f) => (e) => setForm(p => ({ ...p, [f]: e.target.value }))

  const handleSave = async (e) => {
    e.preventDefault()
    const data = { ...form, price: +form.price, stock_qty: +form.stock_qty, reorder_threshold: +form.reorder_threshold }
    if (editing) await updateProduct(editing, data)
    else         await createProduct(data)
    setForm(EMPTY); setEditing(null); load()
  }

  const handleDelete = async (id) => {
    await deleteProduct(id); load()
  }

  const handleAdjust = async (e) => {
    e.preventDefault()
    const res = await adjustStock({ ...adjForm, product_id: +adjForm.product_id, quantity: +adjForm.quantity })
    setMsg(res.detail || 'Stock adjusted'); load()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-green-700">Inventory Management</h1>

      <form onSubmit={handleSave} className="grid grid-cols-2 gap-3 mb-8 max-w-lg">
        <input className="border rounded p-2 text-sm col-span-2" placeholder="Product name" value={form.name}   onChange={set('name')}   required />
        <input className="border rounded p-2 text-sm" placeholder="Category"  value={form.category} onChange={set('category')} required />
        <input className="border rounded p-2 text-sm" placeholder="Price"     type="number" step="0.01" value={form.price} onChange={set('price')} required />
        <input className="border rounded p-2 text-sm" placeholder="Stock qty" type="number" value={form.stock_qty} onChange={set('stock_qty')} required />
        <input className="border rounded p-2 text-sm" placeholder="Reorder threshold" type="number" value={form.reorder_threshold} onChange={set('reorder_threshold')} />
        <input className="border rounded p-2 text-sm col-span-2" placeholder="Image URL (optional)" value={form.image_url} onChange={set('image_url')} />
        <div className="col-span-2 flex gap-2">
          <button className="bg-green-600 text-white px-4 py-1.5 rounded text-sm">{editing ? 'Update' : 'Add Product'}</button>
          {editing && <button type="button" onClick={() => { setForm(EMPTY); setEditing(null) }} className="border px-4 py-1.5 rounded text-sm">Cancel</button>}
        </div>
      </form>

      <form onSubmit={handleAdjust} className="flex gap-2 mb-6 flex-wrap items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">Product ID</label>
          <input className="border rounded p-2 text-sm w-24" type="number" value={adjForm.product_id} onChange={e => setAdjForm(f => ({ ...f, product_id: e.target.value }))} required />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">Type</label>
          <select className="border rounded p-2 text-sm" value={adjForm.adjustment_type} onChange={e => setAdjForm(f => ({ ...f, adjustment_type: e.target.value }))}>
            <option value="add">Add</option>
            <option value="set">Set</option>
            <option value="sale_deduct">Deduct</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">Quantity</label>
          <input className="border rounded p-2 text-sm w-24" type="number" value={adjForm.quantity} onChange={e => setAdjForm(f => ({ ...f, quantity: e.target.value }))} required />
        </div>
        <button className="bg-yellow-500 text-white px-4 py-2 rounded text-sm">Adjust Stock</button>
      </form>
      {msg && <p className="text-green-600 text-sm mb-4">{msg}</p>}

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-green-50 text-left">
              <th className="border px-3 py-2">ID</th>
              <th className="border px-3 py-2">Name</th>
              <th className="border px-3 py-2">Category</th>
              <th className="border px-3 py-2">Price</th>
              <th className="border px-3 py-2">Stock</th>
              <th className="border px-3 py-2">Threshold</th>
              <th className="border px-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="border px-3 py-2">{p.id}</td>
                <td className="border px-3 py-2">{p.name}</td>
                <td className="border px-3 py-2">{p.category}</td>
                <td className="border px-3 py-2">₹{p.price.toFixed(2)}</td>
                <td className={`border px-3 py-2 font-semibold ${p.stock_qty < p.reorder_threshold ? 'text-red-600' : 'text-green-700'}`}>{p.stock_qty}</td>
                <td className="border px-3 py-2">{p.reorder_threshold}</td>
                <td className="border px-3 py-2 flex gap-2">
                  <button onClick={() => { setEditing(p.id); setForm({ name: p.name, category: p.category, price: p.price, stock_qty: p.stock_qty, reorder_threshold: p.reorder_threshold, image_url: p.image_url || '' }) }} className="text-blue-500 hover:underline text-xs">Edit</button>
                  <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:underline text-xs">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
