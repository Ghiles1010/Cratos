import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { AuthProvider } from '@/contexts/AuthContext';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import Login from '@/pages/Login';
import Tasks from '@/pages/Tasks';
import ApiKeys from '@/pages/ApiKeys';
import Health from '@/pages/Health';
import Metrics from '@/pages/Metrics';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Tasks />} />
              <Route path="tasks" element={<Navigate to="/" replace />} />
              <Route path="api-keys" element={<ApiKeys />} />
              <Route path="health" element={<Health />} />
              <Route path="metrics" element={<Metrics />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster
          theme="dark"
          position="top-right"
          toastOptions={{
            style: {
              background: '#18181b',
              border: '1px solid #27272a',
              color: '#e4e4e7',
            },
          }}
        />
      </AuthProvider>
    </QueryClientProvider>
  );
}
