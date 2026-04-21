import { useState } from 'react'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { checkout } from '../api/ordersApi'
import { validateCoupon } from '../api/couponsApi'

export default function CartPage() {
  const { items, removeFromCart, updateQuantity, clearCart, total } = useCart()
  const { token } = useAuth()
  const [couponCode, setCouponCode] = useState('')
  const [discount,   setDiscount]   = useState(0)
  const [receipt,    setReceipt]    = useState(null)
  const [error,      setError]      = useState('')

  const applyCoupon = async () => {
    setError('')
    const res = await validateCoupon({ code: couponCode, order_total: total })
    if (res.valid) setDiscount(res.discount_amount)
    else setError(res.message)
  }

  const handleCheckout = async () => {
    setError('')
    try {
      const order = await checkout({
        items: items.map(i => ({ product_id: i.product.id, quantity: i.quantity })),
        coupon_code: couponCode || null,
      })
      setReceipt(order)
      clearCart()
    } catch {
      setError('Checkout failed. Please try again.')
    }
  }

  if (receipt) return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded-lg shadow text-center">
      <h2 className="text-2xl font-bold text-green-700 mb-2">Order Placed!</h2>
      <p className="text-gray-600">Sale #{receipt.sale_id}</p>
      <p className="text-lg font-semibold mt-2">Total: ₹{receipt.final_amount?.toFixed(2)}</p>
      <button onClick={() => setReceipt(null)} className="mt-4 bg-green-600 text-white px-4 py-2 rounded">
        Continue Shopping
      </button>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-green-700">Your Cart</h1>
      {items.length === 0 ? (
        <p className="text-gray-400">Cart is empty.</p>
      ) : (
        <>
          <div className="flex flex-col gap-3 mb-6">
            {items.map(i => (
              <div key={i.product.id} className="flex items-center justify-between border rounded p-3">
                <span className="font-medium text-sm">{i.product.name}</span>
                <div className="flex items-center gap-2">
                  <button onClick={() => updateQuantity(i.product.id, i.quantity - 1)} className="px-2 border rounded">-</button>
                  <span className="w-6 text-center">{i.quantity}</span>
                  <button onClick={() => updateQuantity(i.product.id, i.quantity + 1)} className="px-2 border rounded">+</button>
                </div>
                <span className="text-green-700 font-semibold">₹{(i.product.price * i.quantity).toFixed(2)}</span>
                <button onClick={() => removeFromCart(i.product.id)} className="text-red-400 hover:text-red-600 text-sm">Remove</button>
              </div>
            ))}
          </div>
          <div className="flex gap-2 mb-4">
            <input
              className="border rounded px-3 py-1.5 text-sm flex-1"
              placeholder="Coupon code"
              value={couponCode}
              onChange={e => setCouponCode(e.target.value.toUpperCase())}
            />
            <button onClick={applyCoupon} className="bg-yellow-400 px-4 py-1.5 rounded text-sm font-medium">Apply</button>
          </div>
          {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
          <div className="text-right mb-4">
            <p className="text-gray-500 text-sm">Subtotal: ₹{total.toFixed(2)}</p>
            {discount > 0 && <p className="text-green-600 text-sm">Discount: -₹{discount.toFixed(2)}</p>}
            <p className="text-lg font-bold">Final: ₹{(total - discount).toFixed(2)}</p>
          </div>
          <button
            onClick={handleCheckout}
            disabled={!token}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white py-2 rounded font-semibold"
          >
            {token ? 'Place Order' : 'Login to Checkout'}
          </button>
        </>
      )}
    </div>
  )
}
