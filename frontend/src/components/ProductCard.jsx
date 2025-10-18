import React from 'react';

const ProductCard = ({ product }) => {
  // Use a placeholder image if the product image is missing or invalid
  const imageUrl = product.image_url && product.image_url.startsWith('http')
    ? product.image_url
    : 'https://via.placeholder.com/300';

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden flex flex-col">
      <img src={imageUrl} alt={product.title} className="w-full h-48 object-cover" />
      <div className="p-4 flex-grow flex flex-col">
        <h3 className="font-bold text-lg mb-2 flex-grow">{product.title}</h3>
        <p className="text-gray-600 text-sm mb-3">{product.gen_description}</p>
        <div className="mt-auto flex justify-between items-center">
            <span className="text-gray-800 font-semibold">${parseFloat(product.price).toFixed(2)}</span>
            <span className="text-xs text-gray-500 uppercase font-medium">{product.brand}</span>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;