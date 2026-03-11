import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from 'react-hot-toast'
import LoginPage from './pages/LoginPage'
import RoleSelectPage from './pages/RoleSelectPage'
import FinanceDataEntry from './pages/finance/DataEntry'
import AuditorAnalysis from './pages/auditor/Analysis'
import ProtectedRoute from './components/auth/ProtectedRoute'

import AuditorLayout from './components/layout/AuditorLayout'
import AuditorChatbot from './pages/auditor/Chatbot'
import AuditorReports from './pages/auditor/Reports'
import AuditorInsights from './pages/auditor/Insights'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#374151',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '14px',
            },
          }}
        />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/role-select" element={
            <ProtectedRoute>
              <RoleSelectPage />
            </ProtectedRoute>
          } />
          <Route path="/finance" element={
            <ProtectedRoute>
              <FinanceDataEntry />
            </ProtectedRoute>
          } />
          
          {/* Auditor Workspace Routes with Layout Wrapper */}
          <Route path="/auditor" element={
            <ProtectedRoute>
              <AuditorLayout>
                <AuditorAnalysis />
              </AuditorLayout>
            </ProtectedRoute>
          } />
          <Route path="/auditor/chat" element={
            <ProtectedRoute>
              <AuditorLayout>
                <AuditorChatbot />
              </AuditorLayout>
            </ProtectedRoute>
          } />
          <Route path="/auditor/reports" element={
            <ProtectedRoute>
              <AuditorLayout>
                <AuditorReports />
              </AuditorLayout>
            </ProtectedRoute>
          } />
          <Route path="/auditor/insights" element={
            <ProtectedRoute>
              <AuditorLayout>
                <AuditorInsights />
              </AuditorLayout>
            </ProtectedRoute>
          } />

          <Route path="*" element={<Navigate to="/role-select" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App