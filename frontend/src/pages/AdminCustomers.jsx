import { useState, useEffect, useCallback } from "react";
import { getAllCustomers, getCustomerHistory } from "../api/customersApi";

const TOKEN_KEY = "kirana_token";

export default function AdminCustomers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [expandedId, setExpandedId] = useState(null);
  const [historyCache, setHistoryCache] = useState({});
  const [historyLoading, setHistoryLoading] = useState(false);

  const token = localStorage.getItem(TOKEN_KEY);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getAllCustomers(token)
      .then((data) => setCustomers(data))
      .catch(() => setError("Failed to load customers."))
      .finally(() => setLoading(false));
  }, [token]);

  const toggleHistory = useCallback(
    async (customerId) => {
      if (expandedId === customerId) {
        setExpandedId(null);
        return;
      }

      setExpandedId(customerId);

      if (historyCache[customerId]) return;

      setHistoryLoading(true);
      try {
        const data = await getCustomerHistory(customerId, token);
        setHistoryCache((prev) => ({ ...prev, [customerId]: data }));
      } catch {
        setHistoryCache((prev) => ({ ...prev, [customerId]: null }));
      } finally {
        setHistoryLoading(false);
      }
    },
    [expandedId, historyCache, token]
  );

  if (loading) {
    return <p className="text-center py-12 text-gray-500">Loading customers…</p>;
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded">{error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Customer Management</h1>

      {customers.length === 0 ? (
        <p className="text-center py-12 text-gray-400">No customers found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Name</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Phone</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Address</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">Total Orders</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">Total Spent (₹)</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => {
                const isExpanded = expandedId === c.id;
                const history = historyCache[c.id];
                const isLoadingThis = isExpanded && historyLoading && !history;

                return (
                  <CustomerRow
                    key={c.id}
                    customer={c}
                    isExpanded={isExpanded}
                    history={history}
                    isLoadingHistory={isLoadingThis}
                    onToggle={toggleHistory}
                  />
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function CustomerRow({ customer, isExpanded, history, isLoadingHistory, onToggle }) {
  const c = customer;

  return (
    <>
      <tr className={`border-t hover:bg-gray-50 ${isExpanded ? "bg-gray-50" : ""}`}>
        <td className="px-4 py-2 text-sm">{c.name}</td>
        <td className="px-4 py-2 text-sm">{c.phone}</td>
        <td className="px-4 py-2 text-sm">{c.address}</td>
        <td className="px-4 py-2 text-sm text-right">{c.total_orders}</td>
        <td className="px-4 py-2 text-sm text-right">₹{Number(c.total_spent).toFixed(2)}</td>
        <td className="px-4 py-2 text-center">
          <button
            onClick={() => onToggle(c.id)}
            className="text-blue-600 hover:underline text-sm"
          >
            {isExpanded ? "Hide History" : "View History"}
          </button>
        </td>
      </tr>

      {isExpanded && (
        <tr>
          <td colSpan={6} className="px-6 py-3 bg-gray-50">
            {isLoadingHistory && (
              <p className="text-gray-500 text-sm py-2">Loading history…</p>
            )}

            {!isLoadingHistory && history === null && (
              <p className="text-red-500 text-sm py-2">Failed to load history.</p>
            )}

            {!isLoadingHistory && history && history.length === 0 && (
              <p className="text-gray-400 text-sm py-2">No purchase history</p>
            )}

            {!isLoadingHistory && history && history.length > 0 && (
              <table className="min-w-full bg-white border rounded text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-3 py-1 text-left font-medium text-gray-600">Date</th>
                    <th className="px-3 py-1 text-left font-medium text-gray-600">Items</th>
                    <th className="px-3 py-1 text-right font-medium text-gray-600">Total</th>
                    <th className="px-3 py-1 text-right font-medium text-gray-600">Discount</th>
                    <th className="px-3 py-1 text-right font-medium text-gray-600">Final Amount</th>
                    <th className="px-3 py-1 text-left font-medium text-gray-600">Coupon Used</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="px-3 py-1">{h.date || "—"}</td>
                      <td className="px-3 py-1">
                        {Array.isArray(h.items) ? h.items.join(", ") : "—"}
                      </td>
                      <td className="px-3 py-1 text-right">₹{Number(h.total).toFixed(2)}</td>
                      <td className="px-3 py-1 text-right">₹{Number(h.discount).toFixed(2)}</td>
                      <td className="px-3 py-1 text-right">₹{Number(h.final_amount).toFixed(2)}</td>
                      <td className="px-3 py-1">{h.coupon_used || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </td>
        </tr>
      )}
    </>
  );
}
