import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute, { ManagerRoute, DirectorRoute } from './components/ProtectedRoute';
import Login from './Login';
import ProductCatalogFixed from './ProductCatalogFixed';
import AddProduct from './AddProduct';
import EditProduct from './EditProduct';
import ProductDetail from './ProductDetail';
import FilterPage from './FilterPage';
import ReadyProducts from './ReadyProducts';
import OrdersAdmin from './OrdersAdmin';
import OrderDetail from './OrderDetail';
import Warehouse from './Warehouse';
import WarehouseItemDetail from './WarehouseItemDetail';
import WarehouseInventory from './WarehouseInventory';
import WarehouseAddInventory from './WarehouseAddInventory';
import ClientsList from './ClientsList';
import ClientDetail from './ClientDetail';
import Profile from './Profile';
import ToastProvider from './components/ToastProvider';

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />

            {/* Protected routes - All authenticated users */}
            <Route path="/" element={
              <ProtectedRoute>
                <ProductCatalogFixed />
              </ProtectedRoute>
            } />
            <Route path="/product/:id" element={
              <ProtectedRoute>
                <ProductDetail />
              </ProtectedRoute>
            } />
            <Route path="/filters" element={
              <ProtectedRoute>
                <FilterPage />
              </ProtectedRoute>
            } />
            <Route path="/ready-products" element={
              <ProtectedRoute>
                <ReadyProducts />
              </ProtectedRoute>
            } />
            <Route path="/orders" element={
              <ProtectedRoute>
                <OrdersAdmin />
              </ProtectedRoute>
            } />
            <Route path="/order/:id" element={
              <ProtectedRoute>
                <OrderDetail />
              </ProtectedRoute>
            } />
            <Route path="/clients" element={
              <ProtectedRoute>
                <ClientsList />
              </ProtectedRoute>
            } />
            <Route path="/client/:id" element={
              <ProtectedRoute>
                <ClientDetail />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />

            {/* Manager/Director only routes */}
            <Route path="/add-product" element={
              <ManagerRoute>
                <AddProduct />
              </ManagerRoute>
            } />
            <Route path="/edit-product/:id" element={
              <ManagerRoute>
                <EditProduct />
              </ManagerRoute>
            } />
            <Route path="/warehouse" element={
              <ManagerRoute>
                <Warehouse />
              </ManagerRoute>
            } />
            <Route path="/warehouse/inventory" element={
              <ManagerRoute>
                <WarehouseInventory />
              </ManagerRoute>
            } />
            <Route path="/warehouse/add-inventory" element={
              <ManagerRoute>
                <WarehouseAddInventory />
              </ManagerRoute>
            } />
            <Route path="/warehouse/:id" element={
              <ManagerRoute>
                <WarehouseItemDetail />
              </ManagerRoute>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;