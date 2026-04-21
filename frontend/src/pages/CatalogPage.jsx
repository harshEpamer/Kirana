import { useState, useEffect } from 'react'
import { getProducts, getCategories } from '../api/catalogApi'
import ProductCard from '../components/ProductCard'

export default function CatalogPage() {
  const [products,   setProducts]   = useState([])
  const [categories, setCategories] = useState([])
  const [category,   setCategory]   = useState('')
  const [search,     setSearch]     = useState('')
  const [loading,    setLoading]    = useState(true)

  useEffect(() => {
    getCategories().then(d => setCategories(d.categories || []))
  }, [])

  useEffect(() => {
    setLoading(true)
    getProducts(category, search)
      .then(setProducts)
      .finally(() => setLoading(false))
  }, [category, search])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-green-700">Product Catalog</h1>
      <div className="flex gap-3 mb-6 flex-wrap">
        <input
          className="border rounded px-3 py-1.5 text-sm w-64"
          placeholder="Search products..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          className="border rounded px-3 py-1.5 text-sm"
          value={category}
          onChange={e => setCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {products.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  )
}
