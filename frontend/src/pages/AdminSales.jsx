import { useState, useEffect, useCallback } from "react";
import { getSalesByDate, getSalesSummary } from "../api/salesApi";

const TOKEN_KEY = "kirana_token";

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

export default function AdminSales() {
  const [date, setDate] = useState(todayStr);
  const [sales, setSales] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const token = localStorage.getItem(TOKEN_KEY);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [salesData, summaryData] = await Promise.all([
        getSalesByDate(date, token),
        getSalesSummary(token),
      ]);
      setSales(salesData);
      setSummary(summaryData);
    } catch (err) {
      setError("Failed to load sales data.");
      setSales([]);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, [date, token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Sales Dashboard</h1>

      {/* Date Picker */}
      <div className="mb-6">
        <label className="mr-2 font-medium">Select Date:</label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="border rounded px-3 py-1"
        />
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      {/* Summary Strip */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white shadow rounded p-4 border-l-4 border-green-500">
            <p className="text-sm text-gray-500">Today's Revenue</p>
            <p className="text-2xl font-bold">₹{summary.today_revenue.toFixed(2)}</p>
          </div>
          <div className="bg-white shadow rounded p-4 border-l-4 border-blue-500">
            <p className="text-sm text-gray-500">Orders</p>
            <p className="text-2xl font-bold">{summary.today_orders}</p>
          </div>
          <div className="bg-white shadow rounded p-4 border-l-4 border-purple-500">
            <p className="text-sm text-gray-500">Top Selling Product</p>
            <p className="text-2xl font-bold">
              {summary.top_product_name || "—"}
            </p>
            {summary.top_product_name && (
              <p className="text-sm text-gray-400">
                {summary.top_product_qty} units
              </p>
            )}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <p className="text-gray-500 text-center py-8">Loading sales…</p>
      )}

      {/* Sales Table */}
      {!loading && sales.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Time</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Customer</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">Items</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">Total</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">Discount</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-gray-600">Final Amount</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm">
                    {sale.sale_time ? new Date(sale.sale_time).toLocaleTimeString() : "—"}
                  </td>
                  <td className="px-4 py-2 text-sm">
                    {sale.customer_name || "Guest"}
                    {sale.customer_phone && (
                      <span className="text-gray-400 ml-1">({sale.customer_phone})</span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-sm">
                    {sale.items.map((i) => i.product_name).join(", ") || "—"}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">₹{sale.total_amount.toFixed(2)}</td>
                  <td className="px-4 py-2 text-sm text-right">₹{sale.discount_amount.toFixed(2)}</td>
                  <td className="px-4 py-2 text-sm text-right font-medium">₹{sale.final_amount.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!loading && sales.length === 0 && !error && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">No sales recorded for this date</p>
        </div>
      )}
    </div>
  );
}
