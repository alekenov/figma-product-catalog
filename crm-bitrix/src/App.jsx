import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ToastProvider from './components/ToastProvider';
import LoadingSpinner from './components/LoadingSpinner';

// Lazy load pages
const OrdersAdmin = React.lazy(() => import('./pages/OrdersAdmin'));
const ProductCatalog = React.lazy(() => import('./pages/ProductCatalog'));
const OrderDetail = React.lazy(() => import('./pages/OrderDetail'));
const ProductDetail = React.lazy(() => import('./pages/ProductDetail'));
const ProductEdit = React.lazy(() => import('./pages/ProductEdit'));
const ProductAdd = React.lazy(() => import('./pages/ProductAdd'));

function App() {
  return (
    <Router>
      <ToastProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/orders" element={<OrdersAdmin />} />
            <Route path="/orders/:orderId" element={<OrderDetail />} />
            <Route path="/products" element={<ProductCatalog />} />
            <Route path="/add-product" element={<ProductAdd />} />
            <Route path="/products/:productId/edit" element={<ProductEdit />} />
            <Route path="/products/:productId" element={<ProductDetail />} />
            <Route path="/" element={<OrdersAdmin />} />
          </Routes>
        </Suspense>
      </ToastProvider>
    </Router>
  );
}

export default App;
