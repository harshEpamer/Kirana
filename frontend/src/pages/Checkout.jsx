import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { placeOrder } from '../api/ordersApi'
import CouponInput from '../components/CouponInput'

export default function Checkout() {
  const { items, clearCart, total } = useCart()
  const { user, token } = useAuth()
  const navigate = useNavigate()

  const [couponCode, setCouponCode] = useState('')
  const [discount, setDiscount] = useState(0)
  const [couponMsg, setCouponMsg] = useState('')
  const [receipt, setReceipt] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const finalAmount = useMemo(() => Math.max(0, total - discount), [total, discount])

  const handleApplyCoupon = async (code) => {
    setCouponCode(code)
    setCouponMsg('')
    setDiscount(0)
    // Coupon will be validated server-side during checkout
    setCouponMsg(`Coupon "${code}" will be applied at checkout`)
  }

  const handlePlaceOrder = async () => {
    if (!user) {
      setError('Please login to place an order')
      return
    }
    if (items.length === 0) {
      setError('Cart is empty')
      return
    }

    setError('')
    setLoading(true)
    try {
      const result = await placeOrder(
        {
          user_id: user.id,
          cart: items.map(i => ({ product_id: i.product.id, quantity: i.quantity })),
          coupon_code: couponCode || null,
        },
        token,
      )
      setReceipt(result)
      setDiscount(result.discount_amount || 0)
      clearCart()
    } catch (err) {
      setError(err.detail || 'Checkout failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (receipt) {
    return (
      <div className="max-w-md mx-auto mt-10 p-6 border rounded-lg shadow text-center">
        <h2 className="text-2xl font-bold text-green-700 mb-2">Order Confirmed!</h2>
        <p className="text-gray-600">Order #{receipt.order_id}</p>
        <div className="mt-4 text-left space-y-1 text-sm">
          <p>Subtotal: ₹{receipt.total_amount.toFixed(2)}</p>
          {receipt.discount_amount > 0 && (
            <p className="text-green-600">Discount: -₹{receipt.discount_amount.toFixed(2)}</p>
          )}
          <p className="text-lg font-semibold">Final: ₹{receipt.final_amount.toFixed(2)}</p>
          {receipt.coupon_applied && (
            <p className="text-xs text-gray-500">Coupon: {receipt.coupon_applied}</p>
          )}
        </div>
        <button
          onClick={() => navigate('/catalog')}
          className="mt-6 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
        >
          Continue Shopping
        </button>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="max-w-md mx-auto mt-10 text-center">
        <p className="text-gray-400 text-lg">Your cart is empty.</p>
        <button
          onClick={() => navigate('/catalog')}
          className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Browse Catalog
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 text-green-700">Checkout</h1>

      {/* Item list table */}
      <table className="w-full text-sm mb-6">
        <thead>
          <tr className="border-b text-left text-gray-600">
            <th className="py-2">Name</th>
            <th className="py-2 text-center">Qty</th>
            <th className="py-2 text-right">Unit Price</th>
            <th className="py-2 text-right">Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {items.map(i => (
            <tr key={i.product.id} className="border-b">
              <td className="py-2 font-medium">{i.product.name}</td>
              <td className="py-2 text-center">{i.quantity}</td>
              <td className="py-2 text-right">₹{i.product.price.toFixed(2)}</td>
              <td className="py-2 text-right font-semibold">₹{(i.product.price * i.quantity).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Coupon */}
      <div className="mb-4">
        <CouponInput onApply={handleApplyCoupon} disabled={loading} />
        {couponMsg && <p className="text-sm text-gray-500 mt-1">{couponMsg}</p>}
      </div>

      {/* Totals */}
      <div className="text-right mb-6 space-y-1">
        <p className="text-gray-500 text-sm">Subtotal: ₹{total.toFixed(2)}</p>
        {discount > 0 && <p className="text-green-600 text-sm">Discount: -₹{discount.toFixed(2)}</p>}
        <p className="text-xl font-bold text-green-700">Total: ₹{finalAmount.toFixed(2)}</p>
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <button
        onClick={handlePlaceOrder}
        disabled={loading}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white py-3 rounded-lg font-semibold text-lg"
      >
        {loading ? 'Placing Order...' : 'Place Order'}
      </button>
    </div>
  )
}
