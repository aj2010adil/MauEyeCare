import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import AppLayout from './AppLayout'
import LoginPage from './LoginPage'
import Dashboard from './Dashboard'
import PatientsPage from './PatientsPage'
import NewVisitPage from './NewVisitPage'
import SettingsPage from './SettingsPage'
import MarketingDashboard from './MarketingDashboard'
import OperationsDashboard from './OperationsDashboard'
import InsightsPage from './InsightsPage'
import PrescriptionsPage from './PrescriptionsPage'
import POSPage from './POSPage'
import InventoryPage from './InventoryPage'
import ShowcasePage from './ShowcasePage'
import { AuthProvider } from './AuthContext'
import AuthGuard from './AuthGuard'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<AuthGuard><AppLayout /></AuthGuard>}>
          <Route index element={<Dashboard />} />
          <Route path="patients" element={<PatientsPage />} />
          <Route path="visits/new" element={<NewVisitPage />} />
          <Route path="pos" element={<POSPage />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="showcase" element={<ShowcasePage />} />
          <Route path="prescriptions" element={<PrescriptionsPage />} />
          <Route path="marketing" element={<MarketingDashboard />} />
          <Route path="operations" element={<OperationsDashboard />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App