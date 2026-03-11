import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { BarChart3, FileText, LogOut, ShieldCheck, ChevronRight } from 'lucide-react'

const RoleSelectPage = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleFinance = () => navigate('/finance')
  const handleAuditor = () => navigate('/auditor')
  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="relative min-h-screen bg-slate-900 flex flex-col justify-center py-12 px-4 overflow-hidden font-sans">
      {/* Animated Background Decorations */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-teal-500/10 rounded-full mix-blend-screen filter blur-3xl animate-blob"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-4000"></div>
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0wIDBoNDB2NDBIMHoiIGZpbGw9Im5vbmUiLz4KPHBhdGggZD0iTTAgMGg0MHYxSDB6bTAgNDBoNDB2MUgweiIgZmlsbD0icmdiYSgyNTUsIDI1NSwgMjU1LCAwLjAzKSIvPgo8cGF0aCBkPSJNMCAwdjQwaDFWMHptNDAgMHY0MGgxVDB6IiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMDMpIi8+Cjwvc3ZnPg==')] opacity-30"></div>

      <div className="relative z-10 max-w-4xl mx-auto w-full animate-fade-in">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/30 ring-1 ring-white/10 animate-slide-up">
              <ShieldCheck className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-extrabold text-white mb-3 tracking-tight">Welcome, {user?.firstName || 'User'}</h1>
          <p className="text-slate-400 text-lg">Select your workspace module to continue</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Finance Role */}
          <button
            onClick={handleFinance}
            className="group glass-card rounded-2xl p-8 text-left hover:scale-[1.02] transition-all duration-300 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-bl-full transition-transform duration-500 group-hover:scale-110"></div>
            
            <div className="relative z-10">
              <div className="w-14 h-14 rounded-xl bg-blue-500/20 flex items-center justify-center mb-6 group-hover:bg-blue-500/30 transition-colors border border-blue-500/30">
                <FileText className="w-7 h-7 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-3 flex items-center justify-between">
                Finance Workspace
                <ChevronRight className="w-6 h-6 text-slate-500 group-hover:text-blue-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </h2>
              <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                Add and manage operational financial transactions in real-time similar to a modern ERP environment.
              </p>
              
              <ul className="text-sm text-slate-300 space-y-3">
                <li className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-3 shadow-[0_0_8px_theme('colors.blue.500')]" />
                  Enter manual transactions
                </li>
                <li className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-3 shadow-[0_0_8px_theme('colors.blue.500')]" />
                  Bulk upload ledgers (CSV)
                </li>
                <li className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-3 shadow-[0_0_8px_theme('colors.blue.500')]" />
                  OCR document scanning
                </li>
              </ul>
            </div>
          </button>

          {/* Auditor Role */}
          <button
            onClick={handleAuditor}
            className="group glass-card rounded-2xl p-8 text-left hover:scale-[1.02] transition-all duration-300 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-teal-500/10 rounded-bl-full transition-transform duration-500 group-hover:scale-110"></div>
            
            <div className="relative z-10">
              <div className="w-14 h-14 rounded-xl bg-teal-500/20 flex items-center justify-center mb-6 group-hover:bg-teal-500/30 transition-colors border border-teal-500/30">
                <BarChart3 className="w-7 h-7 text-teal-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-3 flex items-center justify-between">
                Auditor Workspace
                <ChevronRight className="w-6 h-6 text-slate-500 group-hover:text-teal-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </h2>
              <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                Scan financial datasets orchestrating multiple LLM agents for deep insights and risk detection.
              </p>
              
              <ul className="text-sm text-slate-300 space-y-3">
                <li className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-teal-500 rounded-full mr-3 shadow-[0_0_8px_theme('colors.teal.500')]" />
                  Ingest target datasets
                </li>
                <li className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-teal-500 rounded-full mr-3 shadow-[0_0_8px_theme('colors.teal.500')]" />
                  Step-by-step AI orchestrator flow
                </li>
                <li className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-teal-500 rounded-full mr-3 shadow-[0_0_8px_theme('colors.teal.500')]" />
                  Expandable risk evidence review
                </li>
              </ul>
            </div>
          </button>
        </div>

        <div className="flex justify-center mt-4">
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/50 hover:border-slate-600 transition-all duration-200"
          >
            <LogOut className="w-4 h-4" />
            Secure Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default RoleSelectPage
