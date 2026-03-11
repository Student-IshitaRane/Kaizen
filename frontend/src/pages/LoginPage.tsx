import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Shield, Lock, Mail, ChevronRight } from 'lucide-react'

const LoginPage = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await login({ email, password })
      navigate('/role-select')
    } catch (error) {
      // Error is handled by auth context
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 overflow-hidden font-sans">
      {/* Animated Background Decorations */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-teal-500/20 rounded-full mix-blend-screen filter blur-3xl animate-blob"></div>
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-emerald-500/20 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-32 left-1/2 w-96 h-96 bg-cyan-500/20 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-4000"></div>
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0wIDBoNDB2NDBIMHoiIGZpbGw9Im5vbmUiLz4KPHBhdGggZD0iTTAgMGg0MHYxSDB6bTAgNDBoNDB2MUgweiIgZmlsbD0icmdiYSgyNTUsIDI1NSwgMjU1LCAwLjAzKSIvPgo8cGF0aCBkPSJNMCAwdjQwaDFWMHptNDAgMHY0MGgxVDB6IiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMDMpIi8+Cjwvc3ZnPg==')] opacity-30"></div>

      <div className="relative z-10 sm:mx-auto sm:w-full sm:max-w-md animate-fade-in">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/30 ring-1 ring-white/10">
            <Shield className="h-8 w-8 text-white" />
          </div>
        </div>
        <h2 className="text-center text-3xl font-extrabold tracking-tight text-white mb-2">
          Kaizen Audit Analytics
        </h2>
        <p className="text-center text-sm text-slate-400 max-w-sm mx-auto">
          AI-powered real-time tracking and historical audit analytics for financial risk detection.
        </p>
      </div>

      <div className="relative z-10 mt-8 sm:mx-auto sm:w-full sm:max-w-md animate-slide-up">
        <div className="glass-panel rounded-2xl py-8 px-4 sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300">
                Email address
              </label>
              <div className="mt-2 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="glass-input block w-full pl-10 pr-3 py-3"
                  placeholder="you@company.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300">
                Password
              </label>
              <div className="mt-2 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="glass-input block w-full pl-10 pr-3 py-3"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-700 bg-slate-900/50 text-teal-500 focus:ring-teal-500 focus:ring-offset-slate-900"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-300">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <a href="#" className="font-medium text-teal-400 hover:text-teal-300 transition-colors">
                  Forgot password?
                </a>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full group"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Authenticating...
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full">
                    <span>Sign in securely</span>
                    <ChevronRight className="ml-2 h-4 w-4 opacity-70 group-hover:translate-x-1 transition-transform" />
                  </div>
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-700/50">
            <div className="rounded-xl bg-slate-800/50 border border-slate-700/50 p-4 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-teal-500 rounded-l-xl"></div>
              <div className="flex items-start">
                <div className="flex-shrink-0 mt-0.5">
                  <Shield className="h-5 w-5 text-teal-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-slate-200">Enterprise Security</h3>
                  <div className="mt-1 text-xs text-slate-400">
                    <p>
                      Platform activities are logged and monitored. Authorized personnel only.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-slate-500">
            © {new Date().getFullYear()} Kaizen Audit Analytics.
            <br />
            Powered by Gemini AI.
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage