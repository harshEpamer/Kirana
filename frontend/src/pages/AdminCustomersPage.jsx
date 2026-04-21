import { useEffect, useState, Fragment } from 'react'
import { listCustomers, getPurchaseHistory } from '../api/customersApi'

export default function AdminCustomersPage() {
  const [customers, setCustomers] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [expanded,  setExpanded]  = useState(null) // customerId
  const [histories, setHistories] = useState({})   // { [id]: [records] }

  useEffect(() => {
    setLoading(true)
    listCustomers()
      .then(data => setCustomers(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false))
  }, [])

  const toggle = async (id) => {
    if (expanded === id) {
      setExpanded(null)
      return
    }
    setExpanded(id)
    if (!histories[id]) {
      const data = await getPurchaseHistory(id)
      setHistories(h => ({ ...h, [id]: Array.isArray(data) ? data : [] }))
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-green-700">Customers</h1>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : customers.length === 0 ? (
        <p className="text-gray-400 text-sm">No customers yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-green-50 text-left">
                <th className="border px-3 py-2">ID</th>
                <th className="border px-3 py-2">Name</th>
                <th className="border px-3 py-2">Phone</th>
                <th className="border px-3 py-2">Address</th>
                <th className="border px-3 py-2">Joined</th>
                <th className="border px-3 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {customers.map(c => (
                <Fragment key={c.id}>
                  <tr className="hover:bg-green-50">
                    <td className="border px-3 py-2">{c.id}</td>
                    <td className="border px-3 py-2 font-medium">{c.name}</td>
                    <td className="border px-3 py-2">{c.phone}</td>
                    <td className="border px-3 py-2 text-xs text-gray-500">{c.address}</td>
                    <td className="border px-3 py-2 text-xs text-gray-400">{c.created_at?.slice(0, 10)}</td>
                    <td className="border px-3 py-2">
                      <button
                        onClick={() => toggle(c.id)}
                        className="text-blue-600 hover:underline text-xs"
                      >
                        {expanded === c.id ? 'Hide' : 'View'} History
                      </button>
                    </td>
                  </tr>
                  {expanded === c.id && (
                    <tr>
                      <td colSpan={6} className="border px-4 py-3 bg-gray-50">
                        {histories[c.id] === undefined ? (
                          <p className="text-xs text-gray-400">Loading history…</p>
                        ) : histories[c.id].length === 0 ? (
                          <p className="text-xs text-gray-400">No purchase history.</p>
                        ) : (
                          <table className="w-full text-xs">
                            <thead>
                              <tr className="text-left text-gray-500">
                                <th className="px-2 py-1">Sale #</th>
                                <th className="px-2 py-1">Date</th>
                                <th className="px-2 py-1">Final Amount</th>
                              </tr>
                            </thead>
                            <tbody>
                              {histories[c.id].map(r => (
                                <tr key={r.sale_id}>
                                  <td className="px-2 py-1">#{r.sale_id}</td>
                                  <td className="px-2 py-1">{r.sale_time?.slice(0, 16).replace('T', ' ')}</td>
                                  <td className="px-2 py-1 font-semibold text-green-700">₹{r.final_amount?.toFixed(2)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
