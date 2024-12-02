// components/common/ProductActions.js
import React from 'react';
import { ShoppingCart, X } from 'lucide-react';
import './ProductActions.css';

const ProductActions = ({ 
  onAddToCart, 
  onRemove, 
  showCartButton = true,
  showRemoveButton = true 
}) => {
  return (
    <>
      {showCartButton && (
        <button
          className="product-action-button add-to-cart"
          onClick={(e) => {
            e.stopPropagation();
            onAddToCart();
          }}
          aria-label="장바구니에 추가"
        >
          <ShoppingCart size={18} />
        </button>
      )}
      
      {showRemoveButton && (
        <button
          className="product-action-button remove-item"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          aria-label="삭제"
        >
          <X size={18} />
        </button>
      )}
    </>
  );
};

export default ProductActions;