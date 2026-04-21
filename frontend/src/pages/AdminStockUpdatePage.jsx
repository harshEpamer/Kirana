import { useEffect, useState } from 'react'
import { listProducts, patchStock, getStockLog } from '../api/inventoryApi'

export default function AdminStockUpdatePage() {
  const [products, setProducts] = useState([])
  const [log,      setLog]      = useState([])
  const [productId,setProductId]= useState('')
  const [mode,     setMode]     = useState('add') // 'add' | 'set'
  const [qty,      setQty]      = useState('')
  const [msg,      setMsg]      = useState('')
  const [busy,     setBusy]     = useState(false)

  const loadLog = () => getStockLog().then(d => setLog(Array.isArray(d) ? d : []))

  useEffect(() => {
    listProducts().then(d => {
      const list = Array.isArray(d) ? d : []
      setProducts(list)
      if (list.length > 0) setProductId(String(list[0].id))
    })
    loadLog()
  }, [])

  const flash = (t) => { setMsg(t); setTimeout(() => setMsg(''), 2500) }

  const submit = async (e) => {
    e.preventDefault()
    if (!productId || !qty) return
    setBusy(true)
    try {
      await patchStock(Number(productId), {
        adjustment_type: mode,
        quantity: Number(qty)
      })
      flash(`Stock ${mode === 'add' ? 'added' : 'set'} successfully.`)
      setQty('')
      loadLog()
    } catch (err) {
      flash('Error: ' + err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-green-700">Stock Updates</h1>

      <section className="bg-white border rounded p-4 mb-8 max-w-xl">
        <h2 className="font-semibold mb-3">Manual Adjustment</h2>
        {msg && <div className="bg-blue-100 text-blue-700 px-3 py-2 rounded mb-3 text-sm">{msg}</div>}

        <form onSubmit={submit} className="flex flex-col gap-3">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Product</label>
            <select
              className="border rounded p-2 text-sm w-full"
              value={productId}
              onChange={e => setProductId(e.target.value)}
            >
              {products.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} (current: {p.stock_qty})
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-4 items-center">
            <label className="text-sm flex items-center gap-1">
              <input type="radio" checked={mode === 'add'} onChange={() => setMode('add')} /> Add to stock
            </label>
            <label className="text-sm flex items-center gap-1">
              <input type="radio" checked={mode === 'set'} onChange={() => setMode('set')} /> Set exact qty
            </label>
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">Quantity</label>
            <input
              type="number"
              min="0"
              className="border rounded p-2 text-sm w-full"
              value={qty}
              onChange={e => setQty(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={busy}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white py-2 rounded font-semibold"
          >
            {busy ? 'Updating…' : 'Update Stock'}
          </button>
        </form>
      </section>

      <section>
        <h2 className="font-semibold mb-3 text-gray-700">Stock History</h2>
        {log.length === 0 ? (
          <p className="text-gray-400 text-sm">No adjustments logged yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-50 text-left">
                  <th className="border px-3 py-2">Date</th>
                  <th className="border px-3 py-2">Product</th>
                  <th className="border px-3 py-2">Type</th>
                  <th className="border px-3 py-2">Qty Changed</th>
                  <th className="border px-3 py-2">Reason</th>
                </tr>
              </thead>
              <tbody>
                {log.map(e => (
                  <tr key={e.id} className="hover:bg-gray-50">
                    <td className="border px-3 py-2 text-xs text-gray-500">{e.created_at?.slice(0, 16).replace('T', ' ')}</td>
                    <td className="border px-3 py-2">{e.product_name || `#${e.product_id}`}</td>
                    <td className="border px-3 py-2 text-xs uppercase">{e.adjustment_type}</td>
                    <td className={`border px-3 py-2 font-semibold ${e.quantity_changed >= 0 ? 'text-green-700' : 'text-red-600'}`}>
                      {e.quantity_changed >= 0 ? '+' : ''}{e.quantity_changed}
                    </td>
                    <td className="border px-3 py-2 text-xs text-gray-500">{e.reason || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
