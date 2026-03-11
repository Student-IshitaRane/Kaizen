import { useLocation } from 'react-router-dom'
import { User } from '../../types'
import { Bell, Clock, HelpCircle } from 'lucide-react'
import { format } from 'date-fns'

interface TopHeaderProps {
  user: User
}

const TopHeader = ({ user }: TopHeaderProps) => {
  const location = useLocation()
  const currentTime = new Date()

  const getPageTitle = () => {
    const path = location.pathname
    if (path === '/dashboard') return 'Dashboard'
    if (path === '/transactions') return 'Real-Time Transaction Entry'
    if (path === '/upload') return 'Historical Dataset Upload'
    if (path === '/cases') return 'Flagged Transactions & Case Review'
    if (path === '/reports') return 'Audit Exception Report'
    return 'Audit Analytics Platform'
  }

  const getPageSubtitle = () => {
    const path = location.pathname
    if (path === '/dashboard') {
      return user.role === 'finance' 
        ? 'Submit financial transactions for continuous audit monitoring'
        : 'Monitor financial risk across historical and live data'
    }
    if (path === '/transactions') return 'Submit financial transactions for continuous audit monitoring'
    if (path === '/upload') return 'Upload and process historical financial datasets'
    if (path === '/cases') return 'Review and investigate flagged transactions'
    if (path === '/reports') return 'Generate formal audit exception reports'
    return ''
  }

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Page Title */}
          <div className="flex-1">
            <div className="flex items-center space-x-4">
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{getPageTitle()}</h1>
                {getPageSubtitle() && (
                  <p className="text-sm text-gray-500 mt-0.5">{getPageSubtitle()}</p>
                )}
              </div>
              
              {/* Monitoring Status */}
              {location.pathname === '/dashboard' && user.role === 'auditor' && (
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-50 rounded-lg border border-green-200">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span className="text-sm font-medium text-green-700">Monitoring Active</span>
                </div>
              )}
            </div>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {/* Last Updated */}
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="h-4 w-4" />
              <span>Last updated: {format(currentTime, 'HH:mm')}</span>
            </div>

            {/* Help */}
            <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors">
              <HelpCircle className="h-5 w-5" />
            </button>

            {/* Notifications */}
            <button className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* User Profile (Mobile) */}
            <div className="md:hidden flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-primary-700 font-medium text-sm">
                  {user.firstName?.[0]}{user.lastName?.[0]}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {user.firstName} {user.lastName}
                </p>
                <p className="text-xs text-gray-500 capitalize">{user.role}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default TopHeader