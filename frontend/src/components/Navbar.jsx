import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import CartDrawer from './CartDrawer'

export default function Navbar() {
  const { token, user, isAdmin, logout } = useAuth()
  const { cartCount } = useCart()
  const navigate = useNavigate()
  const [drawerOpen, setDrawerOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <>
      <nav className="bg-green-700 text-white px-6 py-3 flex items-center justify-between shadow">
        <Link to={isAdmin ? '/admin' : '/catalog'} className="text-xl font-bold tracking-wide">
          🛒 Kirana Store
        </Link>

        <div className="flex gap-5 items-center text-sm font-medium">
          {token && !isAdmin && (
            <>
              <Link to="/catalog" className="hover:text-green-200">Catalog</Link>
              <Link to="/history" className="hover:text-green-200">My Orders</Link>
              <button
                onClick={() => setDrawerOpen(true)}
                className="hover:text-green-200 relative"
              >
                Cart
                {cartCount > 0 && (
                  <span className="ml-1 bg-yellow-400 text-green-900 rounded-full px-1.5 py-0.5 text-xs font-bold">
                    {cartCount}
                  </span>
                )}
              </button>
            </>
          )}

          {token && isAdmin && (
            <>
              <Link to="/admin"            className="hover:text-green-200">Dashboard</Link>
              <Link to="/admin/inventory"  className="hover:text-green-200">Inventory</Link>
              <Link to="/admin/stock"      className="hover:text-green-200">Stock Log</Link>
              <Link to="/admin/alerts"     className="hover:text-green-200">Alerts</Link>
              <Link to="/admin/sales"      className="hover:text-green-200">Sales</Link>
              <Link to="/admin/customers"  className="hover:text-green-200">Customers</Link>
            </>
          )}

          {token ? (
            <>
              <span className="text-green-200 text-xs">
                {user?.name} {isAdmin && '(admin)'}
              </span>
              <button onClick={handleLogout} className="hover:text-green-200">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login"    className="hover:text-green-200">Login</Link>
              <Link to="/register" className="hover:text-green-200">Register</Link>
            </>
          )}
        </div>
      </nav>

      <CartDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
    </>
  )
}
