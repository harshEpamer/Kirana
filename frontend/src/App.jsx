import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CatalogPage from './pages/CatalogPage'
import CartPage from './pages/CartPage'
import Checkout from './pages/Checkout'
import PurchaseHistory from './pages/PurchaseHistory'
import AdminDashboard from './pages/AdminDashboard'
import InventoryPage from './pages/InventoryPage'

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <Navbar />
          <div className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/"          element={<Navigate to="/catalog" replace />} />
              <Route path="/login"     element={<LoginPage />} />
              <Route path="/register"  element={<RegisterPage />} />
              <Route path="/catalog"   element={<CatalogPage />} />
              <Route path="/cart"      element={<CartPage />} />
              <Route path="/checkout"  element={<Checkout />} />
              <Route path="/history"   element={<PurchaseHistory />} />
              <Route path="/admin"     element={<AdminDashboard />} />
              <Route path="/inventory" element={<InventoryPage />} />
            </Routes>
          </div>
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  )
}

export default App
