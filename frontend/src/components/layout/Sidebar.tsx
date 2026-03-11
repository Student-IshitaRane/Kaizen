import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { User } from '../../types'
import { 
  LayoutDashboard, 
  FileText, 
  Upload, 
  AlertTriangle, 
  BarChart3,
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

interface SidebarProps {
  user: User
}

const Sidebar = ({ user }: SidebarProps) => {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const { logout } = useAuth()

  const financeNavItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Real-Time Entry', href: '/transactions', icon: FileText },
    { name: 'Recent Transactions', href: '/transactions/recent', icon: FileText },
  ]

  const auditorNavItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Upload Datasets', href: '/upload', icon: Upload },
    { name: 'Flagged Cases', href: '/cases', icon: AlertTriangle },
    { name: 'Exception Reports', href: '/reports', icon: BarChart3 },
  ]

  const navItems = user.role === 'finance' ? financeNavItems : auditorNavItems

  return (
    <>
      <div className={`fixed inset-y-0 left-0 z-50 bg-white border-r border-gray-200 transition-all duration-300 ${collapsed ? 'w-20' : 'w-64'}`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center h-16 px-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
                <span className="text-white font-semibold">AI</span>
              </div>
              {!collapsed && (
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">Audit Analytics</h1>
                  <p className="text-xs text-gray-500">Enterprise Platform</p>
                </div>
              )}
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto scrollbar-thin">
            {navItems.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600' 
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }
                    ${collapsed ? 'justify-center' : ''}
                  `}
                >
                  <item.icon className={`h-5 w-5 ${collapsed ? '' : 'mr-3'}`} />
                  {!collapsed && <span>{item.name}</span>}
                </NavLink>
              )
            })}
          </nav>

          {/* User & Collapse */}
          <div className="border-t border-gray-200 p-4">
            <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'}`}>
              {!collapsed && (
                <div className="flex items-center space-x-3">
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
              )}
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCollapsed(!collapsed)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
                  title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                  {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                </button>
                
                {collapsed && (
                  <button
                    onClick={logout}
                    className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
                    title="Logout"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
            
            {!collapsed && (
              <button
                onClick={logout}
                className="mt-4 w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default Sidebar