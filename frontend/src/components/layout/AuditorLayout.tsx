import { ReactNode, useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import {
  Activity,
  BarChart3,
  MessageSquare,
  FileText,
  LogOut,
  Bell,
  Menu,
  X,
  Search
} from 'lucide-react'

interface AuditorLayoutProps {
  children: ReactNode
}

const AuditorLayout = ({ children }: AuditorLayoutProps) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navigation = [
    { name: 'Upload & Analyze', href: '/auditor', icon: Activity },
    { name: 'AI Chatbot', href: '/auditor/chat', icon: MessageSquare },
    { name: 'Reports', href: '/auditor/reports', icon: FileText },
    { name: 'Insights', href: '/auditor/insights', icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-teal-500/30 flex overflow-hidden">

      {/* Background Gradients */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[10%] left-[-10%] w-[40%] h-[40%] bg-teal-600/10 rounded-full mix-blend-screen filter blur-[120px] animate-pulse-slow"></div>
        <div className="absolute bottom-[-10%] right-[10%] w-[30%] h-[50%] bg-emerald-600/10 rounded-full mix-blend-screen filter blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-72 h-screen glass-panel border-r border-slate-700/50 sticky top-0 z-20">
        <div className="p-6 flex items-center justify-between border-b border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-teal-500/20 border border-teal-500/30 flex items-center justify-center shadow-[0_0_15px_theme('colors.teal.500/0.2')]">
              <Activity className="w-5 h-5 text-teal-400" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">AI Auditor</h1>
              <span className="text-[10px] font-medium text-teal-400 uppercase tracking-widest block">Enterprise Suite</span>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 px-3">Main Navigation</div>
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${isActive
                  ? 'bg-teal-500/10 border border-teal-500/30 text-teal-400 shadow-[0_0_15px_theme("colors.teal.500/0.1")]'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border border-transparent'
                  }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-teal-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span className="font-medium">{item.name}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-teal-400 shadow-[0_0_8px_theme('colors.teal.400')] animate-pulse" />
                )}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-slate-700/50">
          <button
            onClick={() => navigate('/role-select')}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-xl transition-all border border-transparent hover:border-slate-700"
          >
            <Menu className="w-5 h-5" />
            <span>Switch Module</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">

        {/* Top Header */}
        <header className="h-20 glass-panel border-b border-slate-700/50 flex items-center justify-between px-4 sm:px-6 lg:px-8">

          <div className="flex items-center gap-4 lg:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="w-8 h-8 rounded-lg bg-teal-500/20 border border-teal-500/30 flex items-center justify-center">
              <Activity className="w-4 h-4 text-teal-400" />
            </div>
          </div>

          <div className="hidden lg:flex items-center bg-slate-800/50 border border-slate-700 rounded-full px-4 py-2 w-96 backdrop-blur-md focus-within:border-teal-500/50 focus-within:ring-1 focus-within:ring-teal-500/50 transition-all">
            <Search className="w-4 h-4 text-slate-500 mr-3" />
            <input
              type="text"
              placeholder="Search records, flags, or insights..."
              className="bg-transparent border-none outline-none text-sm text-white placeholder-slate-500 w-full"
            />
          </div>

          <div className="flex items-center gap-4 sm:gap-6">
            <button className="relative p-2 text-slate-400 hover:text-white transition-colors rounded-full hover:bg-slate-800">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-slate-900"></span>
            </button>

            <div className="h-8 w-px bg-slate-700/50 hidden sm:block"></div>

            <div className="flex items-center gap-3">
              <div className="hidden sm:block text-right">
                <div className="text-sm font-semibold text-white">{user?.firstName || 'Auditor'}</div>
                <div className="text-[10px] text-teal-400 uppercase tracking-wider">{user?.role || 'Lead Analyst'}</div>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-teal-500 to-emerald-600 p-0.5 shadow-lg shadow-teal-500/20 cursor-pointer">
                <div className="w-full h-full bg-slate-900 rounded-full flex items-center justify-center border-2 border-slate-900">
                  <span className="text-sm font-bold text-white">{user?.firstName?.charAt(0) || 'A'}</span>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="hidden sm:flex items-center gap-2 p-2 text-slate-400 hover:text-red-400 transition-colors rounded-lg hover:bg-red-500/10 ml-2"
              title="Secure Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto w-full">
          {children}
        </main>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm" onClick={() => setIsMobileMenuOpen(false)}></div>
          <div className="absolute top-0 left-0 w-72 h-full glass-panel border-r border-slate-700 animate-slide-up flex flex-col shadow-2xl">
            <div className="p-6 flex items-center justify-between border-b border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-teal-500/20 border border-teal-500/30 flex items-center justify-center">
                  <Activity className="w-4 h-4 text-teal-400" />
                </div>
                <h1 className="text-lg font-bold text-white tracking-tight">AI Auditor</h1>
              </div>
              <button onClick={() => setIsMobileMenuOpen(false)} className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <nav className="flex-1 p-4 space-y-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${location.pathname === item.href
                    ? 'bg-teal-500/10 border border-teal-500/30 text-teal-400'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              ))}
            </nav>
            <div className="p-6 border-t border-slate-700/50">
              <button onClick={handleLogout} className="w-full btn-secondary text-red-400 hover:text-red-300 hover:bg-red-500/10 border-red-500/20 flex items-center justify-center gap-2">
                <LogOut className="w-4 h-4" /> Sign Out
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}

export default AuditorLayout
