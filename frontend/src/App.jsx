import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import Navbar from './components/Navbar'
import AuthGuard from './components/AuthGuard'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CatalogPage from './pages/CatalogPage'
import CartPage from './pages/CartPage'
import Checkout from './pages/Checkout'
import PurchaseHistory from './pages/PurchaseHistory'
import AdminDashboard from './pages/AdminDashboard'
import InventoryPage from './pages/InventoryPage'
import AdminStockUpdatePage from './pages/AdminStockUpdatePage'
import AdminAlertsPage from './pages/AdminAlertsPage'
import AdminSalesPage from './pages/AdminSalesPage'
import AdminCustomersPage from './pages/AdminCustomersPage'

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <Navbar />
          <div className="container mx-auto px-4 py-6">
            <Routes>
              {/* Public */}
              <Route path="/"         element={<Navigate to="/catalog" replace />} />
              <Route path="/login"    element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* User (any logged-in user) */}
              <Route path="/catalog"  element={<CatalogPage />} />
              <Route path="/cart"     element={<AuthGuard><CartPage /></AuthGuard>} />
              <Route path="/checkout" element={<AuthGuard><Checkout /></AuthGuard>} />
              <Route path="/history"  element={<AuthGuard><PurchaseHistory /></AuthGuard>} />

              {/* Admin-only */}
              <Route path="/admin"            element={<AuthGuard adminOnly><AdminDashboard /></AuthGuard>} />
              <Route path="/admin/inventory"  element={<AuthGuard adminOnly><InventoryPage /></AuthGuard>} />
              <Route path="/admin/stock"      element={<AuthGuard adminOnly><AdminStockUpdatePage /></AuthGuard>} />
              <Route path="/admin/alerts"     element={<AuthGuard adminOnly><AdminAlertsPage /></AuthGuard>} />
              <Route path="/admin/sales"      element={<AuthGuard adminOnly><AdminSalesPage /></AuthGuard>} />
              <Route path="/admin/customers"  element={<AuthGuard adminOnly><AdminCustomersPage /></AuthGuard>} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/catalog" replace />} />
            </Routes>
          </div>
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  )
}

export default App
