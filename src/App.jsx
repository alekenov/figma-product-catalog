import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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
      <Router>
        <Routes>
          <Route path="/" element={<ProductCatalogFixed />} />
          <Route path="/add-product" element={<AddProduct />} />
          <Route path="/edit-product/:id" element={<EditProduct />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/filters" element={<FilterPage />} />
          <Route path="/ready-products" element={<ReadyProducts />} />
          <Route path="/orders" element={<OrdersAdmin />} />
          <Route path="/order/:id" element={<OrderDetail />} />
          <Route path="/warehouse" element={<Warehouse />} />
          <Route path="/warehouse/inventory" element={<WarehouseInventory />} />
          <Route path="/warehouse/add-inventory" element={<WarehouseAddInventory />} />
          <Route path="/warehouse/:id" element={<WarehouseItemDetail />} />
          <Route path="/clients" element={<ClientsList />} />
          <Route path="/client/:phone" element={<ClientDetail />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Router>
    </ToastProvider>
  );
}

export default App;