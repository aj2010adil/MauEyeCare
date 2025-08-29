import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
//import AppLayout from './AppLayout'
import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import PatientsPage from './components/PatientsPage'
import NewVisitPage from './components/NewVisitPage'
import SettingsPage from './components/SettingsPage'
import MarketingDashboard from './components/MarketingDashboard'
import OperationsDashboard from './components/OperationsDashboard'
import InsightsPage from './components/InsightsPage'
import PrescriptionsPage from './components/PrescriptionsPage'
import POSPage from './components/POSPage'
import InventoryPage from './components/InventoryPage'
import ShowcasePage from './components/ShowcasePage'
import { AuthProvider } from './components/AuthContext'
//import AuthGuard from './AuthGuard'
import RoleGuard from './components/RoleGuard'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Dashboard />} />
          <Route path="patients" element={<PatientsPage />} />
          <Route path="visits/new" element={<NewVisitPage />} />
          <Route path="pos" element={<POSPage />} />
          <Route path="inventory" element={<RoleGuard roles={["admin","doctor"]}><InventoryPage /></RoleGuard>} />
          <Route path="showcase" element={<ShowcasePage />} />
          <Route path="prescriptions" element={<PrescriptionsPage />} />
          <Route path="marketing" element={<MarketingDashboard />} />
          <Route path="operations" element={<OperationsDashboard />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="settings" element={<RoleGuard roles={["admin"]}><SettingsPage /></RoleGuard>} />
      
      </Routes>
    </AuthProvider>
  )
}

export default App