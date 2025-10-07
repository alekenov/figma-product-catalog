import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute, { ManagerRoute, DirectorRoute, SuperadminRoute } from './components/ProtectedRoute';
import ToastProvider from './components/ToastProvider';
import LoadingSpinner from './components/LoadingSpinner';

// Direct imports for frequently used components
import Login from './Login';
import Register from './Register';

// Lazy load all route components
const ProductCatalogFixed = React.lazy(() => import('./ProductCatalogFixed'));
const AddProduct = React.lazy(() => import('./AddProduct'));
const EditProduct = React.lazy(() => import('./EditProduct'));
const ProductDetail = React.lazy(() => import('./ProductDetail'));
const FilterPage = React.lazy(() => import('./FilterPage'));
const ReadyProducts = React.lazy(() => import('./ReadyProducts'));
const OrdersAdmin = React.lazy(() => import('./OrdersAdmin'));
const OrderDetail = React.lazy(() => import('./OrderDetail'));
const CreateOrder = React.lazy(() => import('./CreateOrder'));
const CreateOrderCustomer = React.lazy(() => import('./CreateOrderCustomer'));
const CreateOrderReview = React.lazy(() => import('./CreateOrderReview'));
const Warehouse = React.lazy(() => import('./Warehouse'));
const WarehouseItemDetail = React.lazy(() => import('./WarehouseItemDetail'));
const WarehouseInventory = React.lazy(() => import('./WarehouseInventory'));
const WarehouseAddInventory = React.lazy(() => import('./WarehouseAddInventory'));
const ClientsList = React.lazy(() => import('./ClientsList'));
const AddClient = React.lazy(() => import('./AddClient'));
const ClientDetail = React.lazy(() => import('./ClientDetail'));
const Profile = React.lazy(() => import('./Profile'));

// Superadmin components
const Superadmin = React.lazy(() => import('./Superadmin'));
const ProductsList = React.lazy(() => import('./ProductsList'));
const SuperadminOrdersList = React.lazy(() => import('./superadmin/SuperadminOrdersList'));
const SuperadminOrderDetail = React.lazy(() => import('./superadmin/SuperadminOrderDetail'));
const ShopsList = React.lazy(() => import('./superadmin/ShopsList'));
const ShopDetail = React.lazy(() => import('./superadmin/ShopDetail'));
const UserManagement = React.lazy(() => import('./superadmin/UserManagement'));

// Configure React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (garbage collection time)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <Router>
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

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
                <Route path="/orders/:orderId" element={
                  <ProtectedRoute>
                    <OrderDetail />
                  </ProtectedRoute>
                } />
                <Route path="/create-order" element={
                  <ProtectedRoute>
                    <CreateOrder />
                  </ProtectedRoute>
                } />
                <Route path="/create-order/customer" element={
                  <ProtectedRoute>
                    <CreateOrderCustomer />
                  </ProtectedRoute>
                } />
                <Route path="/create-order/review" element={
                  <ProtectedRoute>
                    <CreateOrderReview />
                  </ProtectedRoute>
                } />
                <Route path="/clients" element={
                  <ProtectedRoute>
                    <ClientsList />
                  </ProtectedRoute>
                } />
                <Route path="/clients/add" element={
                  <ProtectedRoute>
                    <AddClient />
                  </ProtectedRoute>
                } />
                <Route path="/clients/:clientId" element={
                  <ProtectedRoute>
                    <ClientDetail />
                  </ProtectedRoute>
                } />
                <Route path="/profile" element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                } />

                {/* Manager-only routes */}
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
                <Route path="/warehouse/:itemId" element={
                  <ManagerRoute>
                    <WarehouseItemDetail />
                  </ManagerRoute>
                } />
                <Route path="/warehouse/add" element={
                  <ManagerRoute>
                    <WarehouseAddInventory />
                  </ManagerRoute>
                } />

                {/* Director-only routes */}
                <Route path="/warehouse/inventory-check" element={
                  <DirectorRoute>
                    <WarehouseInventory />
                  </DirectorRoute>
                } />

                {/* Superadmin-only routes */}
                <Route path="/superadmin" element={
                  <SuperadminRoute>
                    <Superadmin />
                  </SuperadminRoute>
                } />
                <Route path="/superadmin/products" element={
                  <SuperadminRoute>
                    <ProductsList />
                  </SuperadminRoute>
                } />
                <Route path="/superadmin/orders" element={
                  <SuperadminRoute>
                    <SuperadminOrdersList />
                  </SuperadminRoute>
                } />
                <Route path="/superadmin/orders/:orderId" element={
                  <SuperadminRoute>
                    <SuperadminOrderDetail />
                  </SuperadminRoute>
                } />
                <Route path="/superadmin/shops" element={
                  <SuperadminRoute>
                    <ShopsList />
                  </SuperadminRoute>
                } />
                <Route path="/superadmin/shops/:shopId" element={
                  <SuperadminRoute>
                    <ShopDetail />
                  </SuperadminRoute>
                } />
                <Route path="/superadmin/users" element={
                  <SuperadminRoute>
                    <UserManagement />
                  </SuperadminRoute>
                } />
              </Routes>
            </Suspense>
          </Router>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
}

export default App;