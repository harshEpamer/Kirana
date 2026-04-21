import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Navbar() {
  const { token, logout } = useAuth()
  const { items } = useCart()
  const cartCount = items.reduce((s, i) => s + i.quantity, 0)

  return (
    <nav className="bg-green-700 text-white px-6 py-3 flex items-center justify-between">
      <Link to="/catalog" className="text-xl font-bold tracking-wide">
        🛒 Kirana Store
      </Link>
      <div className="flex gap-6 items-center text-sm font-medium">
        <Link to="/catalog" className="hover:text-green-200">Catalog</Link>
        <Link to="/cart" className="hover:text-green-200 relative">
          Cart
          {cartCount > 0 && (
            <span className="ml-1 bg-yellow-400 text-green-900 rounded-full px-1.5 py-0.5 text-xs font-bold">
              {cartCount}
            </span>
          )}
        </Link>
        <Link to="/admin" className="hover:text-green-200">Admin</Link>
        <Link to="/inventory" className="hover:text-green-200">Inventory</Link>
        {token ? (
          <button onClick={logout} className="hover:text-green-200">Logout</button>
        ) : (
          <Link to="/login" className="hover:text-green-200">Login</Link>
        )}
      </div>
    </nav>
  )
}
