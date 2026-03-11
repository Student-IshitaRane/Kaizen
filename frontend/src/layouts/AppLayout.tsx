import { Outlet } from 'react-router-dom'
import Sidebar from '../components/layout/Sidebar'
import TopHeader from '../components/layout/TopHeader'
import { useAuth } from '../contexts/AuthContext'

const AppLayout = () => {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar user={user!} />
      <div className="lg:pl-64">
        <TopHeader user={user!} />
        <main className="py-6 px-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppLayout