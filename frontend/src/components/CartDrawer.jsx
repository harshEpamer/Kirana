import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'

export default function CartDrawer({ open, onClose }) {
  const { items, updateQuantity, removeFromCart, total } = useCart()
  const navigate = useNavigate()

  if (!open) return null

  const goToCheckout = () => {
    onClose()
    navigate('/cart')
  }

  return (
    <>
      <div className="fixed inset-0 bg-black/40 z-40" onClick={onClose} />
      <aside className="fixed top-0 right-0 h-full w-80 bg-white shadow-xl z-50 flex flex-col">
        <header className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-bold text-green-700">Your Cart</h2>
          <button onClick={onClose} className="text-2xl leading-none text-gray-400 hover:text-gray-700">×</button>
        </header>

        <div className="flex-1 overflow-y-auto p-4">
          {items.length === 0 ? (
            <p className="text-gray-400 text-sm text-center mt-8">Your cart is empty.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {items.map(i => (
                <li key={i.product.id} className="border rounded p-2 text-sm">
                  <div className="font-medium">{i.product.name}</div>
                  <div className="text-xs text-gray-500">₹{i.product.price.toFixed(2)} each</div>
                  <div className="flex items-center justify-between mt-1">
                    <div className="flex items-center gap-1">
                      <button onClick={() => updateQuantity(i.product.id, i.quantity - 1)} className="px-2 border rounded">-</button>
                      <span className="w-6 text-center">{i.quantity}</span>
                      <button onClick={() => updateQuantity(i.product.id, i.quantity + 1)} className="px-2 border rounded">+</button>
                    </div>
                    <span className="font-semibold text-green-700">₹{(i.product.price * i.quantity).toFixed(2)}</span>
                    <button onClick={() => removeFromCart(i.product.id)} className="text-xs text-red-400 hover:text-red-600">×</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {items.length > 0 && (
          <footer className="border-t p-4">
            <div className="flex justify-between font-semibold mb-3">
              <span>Subtotal</span>
              <span>₹{total.toFixed(2)}</span>
            </div>
            <button
              onClick={goToCheckout}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-semibold"
            >
              Proceed to Checkout
            </button>
          </footer>
        )}
      </aside>
    </>
  )
}
