import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CartProvider } from './contexts/CartContext';
import HomePage from './pages/HomePage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import Cart2Page from './pages/Cart2Page';
import OrderStatusPage from './pages/OrderStatusPage';
import KorizinaPage from './pages/KorizinaPage';
import FeaturedDemo from './pages/FeaturedDemo';
import './App.css';

function App() {
  return (
    <CartProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/product/:id" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/cart2" element={<Cart2Page />} />
          <Route path="/korizina" element={<KorizinaPage />} />
          <Route path="/status/:id" element={<OrderStatusPage />} />
          <Route path="/featured-demo" element={<FeaturedDemo />} />
        </Routes>
      </Router>
    </CartProvider>
  );
}

export default App;