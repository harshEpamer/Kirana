import { useCart } from '../context/CartContext'

export default function ProductCard({ product }) {
  const { addToCart } = useCart()

  return (
    <div className="border rounded-lg p-4 flex flex-col gap-2 shadow-sm hover:shadow-md transition-shadow bg-white">
      {product.image_url && (
        <img src={product.image_url} alt={product.name} className="h-32 object-contain rounded" />
      )}
      <h3 className="font-semibold text-gray-800 text-sm">{product.name}</h3>
      <p className="text-xs text-gray-500">{product.category}</p>
      <p className="text-green-700 font-bold">₹{product.price.toFixed(2)}</p>
      <p className="text-xs text-gray-400">Stock: {product.stock_qty}</p>
      <button
        onClick={() => addToCart(product)}
        disabled={product.stock_qty === 0}
        className="mt-auto bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white text-sm py-1.5 rounded"
      >
        {product.stock_qty === 0 ? 'Out of Stock' : 'Add to Cart'}
      </button>
    </div>
  )
}
