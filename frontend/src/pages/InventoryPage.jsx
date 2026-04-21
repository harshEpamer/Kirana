import { useState, useEffect } from 'react'
import { listProducts, createProduct, updateProduct, deleteProduct, adjustStock, getLowStock, bulkInsert, getReorderList } from '../api/inventoryApi'

const EMPTY = { name: '', category: '', price: '', stock_qty: '', reorder_threshold: '10', image_url: '' }
const TABS = ['Products', 'Low Stock', 'Bulk Upload', 'Reorder List']

export default function InventoryPage() {
  const [products, setProducts] = useState([])
  const [form,     setForm]     = useState(EMPTY)
  const [editing,  setEditing]  = useState(null)
  const [adjForm,  setAdjForm]  = useState({ product_id: '', adjustment_type: 'add', quantity: '' })
  const [msg,      setMsg]      = useState('')
  const [tab,      setTab]      = useState('Products')

  // Low stock
  const [lowStock, setLowStock] = useState([])

  // Bulk upload
  const [bulkText, setBulkText] = useState('')
  const [bulkMsg,  setBulkMsg]  = useState('')

  // Reorder
  const [reorder,  setReorder]  = useState([])

  const load = () => listProducts().then(setProducts)
  useEffect(() => { load() }, [])

  useEffect(() => {
    if (tab === 'Low Stock')    getLowStock().then(setLowStock)
    if (tab === 'Reorder List') getReorderList().then(setReorder)
  }, [tab])

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

  const handleBulk = async (e) => {
    e.preventDefault()
    setBulkMsg('')
    try {
      const parsed = JSON.parse(bulkText)
      if (!Array.isArray(parsed)) { setBulkMsg('JSON must be an array of products'); return }
      const res = await bulkInsert(parsed)
      setBulkMsg(`Successfully created ${res.created} products`)
      setBulkText('')
      load()
    } catch {
      setBulkMsg('Invalid JSON — must be an array of product objects')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-green-700">Inventory Management</h1>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium rounded-t ${tab === t ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {t}
            {t === 'Low Stock' && lowStock.length > 0 && <span className="ml-1.5 bg-red-500 text-white rounded-full px-1.5 py-0.5 text-xs">{lowStock.length}</span>}
          </button>
        ))}
      </div>

      {/* ── Products Tab ─────────────────────────────────────────────── */}
      {tab === 'Products' && <>
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
      </>}

      {/* ── Low Stock Tab ────────────────────────────────────────────── */}
      {tab === 'Low Stock' && <>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-red-600">Low Stock Alerts</h2>
          <button onClick={() => getLowStock().then(setLowStock)} className="text-sm text-green-600 hover:underline">Refresh</button>
        </div>
        {lowStock.length === 0 ? (
          <p className="text-gray-500 text-sm">All products are above their reorder threshold.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-red-50 text-left">
                  <th className="border px-3 py-2">ID</th>
                  <th className="border px-3 py-2">Name</th>
                  <th className="border px-3 py-2">Category</th>
                  <th className="border px-3 py-2">Stock</th>
                  <th className="border px-3 py-2">Threshold</th>
                  <th className="border px-3 py-2">Deficit</th>
                </tr>
              </thead>
              <tbody>
                {lowStock.map(p => (
                  <tr key={p.id} className="hover:bg-red-50/50">
                    <td className="border px-3 py-2">{p.id}</td>
                    <td className="border px-3 py-2 font-medium">{p.name}</td>
                    <td className="border px-3 py-2">{p.category}</td>
                    <td className="border px-3 py-2 text-red-600 font-bold">{p.stock_qty}</td>
                    <td className="border px-3 py-2">{p.reorder_threshold}</td>
                    <td className="border px-3 py-2 text-red-600">{p.reorder_threshold - p.stock_qty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </>}

      {/* ── Bulk Upload Tab ──────────────────────────────────────────── */}
      {tab === 'Bulk Upload' && <>
        <h2 className="text-lg font-semibold text-green-700 mb-2">Bulk Product Upload</h2>
        <p className="text-xs text-gray-500 mb-3">Paste a JSON array of products. Each object needs: name, category, price. Optional: stock_qty, reorder_threshold, image_url.</p>
        <form onSubmit={handleBulk}>
          <textarea
            className="w-full border rounded p-3 text-sm font-mono h-48 mb-3"
            placeholder={`[\n  { "name": "Rice", "category": "Grocery", "price": 60, "stock_qty": 100 },\n  { "name": "Dal", "category": "Grocery", "price": 120, "stock_qty": 50 }\n]`}
            value={bulkText}
            onChange={e => setBulkText(e.target.value)}
            required
          />
          <button className="bg-green-600 text-white px-5 py-2 rounded text-sm">Upload Products</button>
        </form>
        {bulkMsg && <p className={`mt-3 text-sm ${bulkMsg.startsWith('Successfully') ? 'text-green-600' : 'text-red-600'}`}>{bulkMsg}</p>}
      </>}

      {/* ── Reorder List Tab ─────────────────────────────────────────── */}
      {tab === 'Reorder List' && <>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-green-700">Reorder Suggestions</h2>
          <button onClick={() => getReorderList().then(setReorder)} className="text-sm text-green-600 hover:underline">Refresh</button>
        </div>
        {reorder.length === 0 ? (
          <p className="text-gray-500 text-sm">No products need reordering at this time.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-green-50 text-left">
                  <th className="border px-3 py-2">Product ID</th>
                  <th className="border px-3 py-2">Name</th>
                  <th className="border px-3 py-2">Category</th>
                  <th className="border px-3 py-2">Current Stock</th>
                  <th className="border px-3 py-2">Threshold</th>
                  <th className="border px-3 py-2">Suggested Order Qty</th>
                </tr>
              </thead>
              <tbody>
                {reorder.map(r => (
                  <tr key={r.product_id} className="hover:bg-gray-50">
                    <td className="border px-3 py-2">{r.product_id}</td>
                    <td className="border px-3 py-2 font-medium">{r.name}</td>
                    <td className="border px-3 py-2">{r.category}</td>
                    <td className="border px-3 py-2 text-red-600 font-bold">{r.stock_qty}</td>
                    <td className="border px-3 py-2">{r.reorder_threshold}</td>
                    <td className="border px-3 py-2 text-green-700 font-bold">{r.suggested_qty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </>}
    </div>
  )
}
