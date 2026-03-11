import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { ArrowLeft, Plus, Upload, FileText, LayoutDashboard, LogOut, CheckCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../services/api/auth'

const FinanceDataEntry = () => {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [activeTab, setActiveTab] = useState<'form' | 'upload' | 'ocr'>('form')
  const [formData, setFormData] = useState({
    invoice_id: '',
    vendor_id: '',
    vendor_name: '',
    amount: '',
    date: '',
    department: '',
    description: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      const response = await api.post('/transactions', {
        ...formData,
        amount: parseFloat(formData.amount),
      })
      
      if (response.status === 201 || response.status === 200) {
        toast.success('Transaction added successfully')
        setFormData({
          invoice_id: '',
          vendor_id: '',
          vendor_name: '',
          amount: '',
          date: '',
          department: '',
          description: '',
        })
      } else {
        toast.error('Failed to add transaction')
      }
    } catch (error: any) {
      toast.error(error.message || 'Error adding transaction')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-500/30">
      {/* Background Gradients */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 rounded-full mix-blend-screen filter blur-[100px] animate-blob space-y-4"></div>
        <div className="absolute top-[20%] right-[-10%] w-[30%] h-[50%] bg-indigo-600/10 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 glass-panel border-b border-slate-700/50 sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/role-select')}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                <LayoutDashboard className="w-5 h-5 text-blue-400" />
              </div>
              <h1 className="text-xl font-bold font-sans tracking-tight text-white flex flex-col">
                Finance Workspace
                <span className="text-xs font-medium text-blue-400 uppercase tracking-wider">Enterprise ERP</span>
              </h1>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Secure Logout</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12 animate-fade-in">
        
        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-slate-800/40 p-2 rounded-xl backdrop-blur-sm border border-slate-700/50 inline-flex">
          <button
            onClick={() => setActiveTab('form')}
            className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
              activeTab === 'form'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <Plus className="w-4 h-4" />
            Manual Entry
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
              activeTab === 'upload'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <Upload className="w-4 h-4" />
            Bulk Upload
          </button>
          <button
            onClick={() => setActiveTab('ocr')}
            className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
              activeTab === 'ocr'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <FileText className="w-4 h-4" />
            OCR Scan
          </button>
        </div>

        <div className="animate-slide-up">
          {/* Manual Entry Form */}
          {activeTab === 'form' && (
            <div className="glass-card rounded-2xl p-6 sm:p-10 max-w-4xl border-t border-t-white/10">
              <div className="mb-8 border-b border-slate-700/50 pb-6">
                <h2 className="text-2xl font-bold text-white mb-2">New Transaction</h2>
                <p className="text-slate-400 text-sm">Enter transaction details into the general ledger system.</p>
              </div>

              <form onSubmit={handleFormSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-300">
                      Invoice ID
                    </label>
                    <input
                      type="text"
                      name="invoice_id"
                      value={formData.invoice_id}
                      onChange={handleFormChange}
                      required
                      className="glass-input w-full px-4 py-2.5"
                      placeholder="e.g. INV-2024-001"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-300">
                      Vendor ID
                    </label>
                    <input
                      type="text"
                      name="vendor_id"
                      value={formData.vendor_id}
                      onChange={handleFormChange}
                      required
                      className="glass-input w-full px-4 py-2.5"
                      placeholder="e.g. V-001"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">
                    Vendor Name
                  </label>
                  <input
                    type="text"
                    name="vendor_name"
                    value={formData.vendor_name}
                    onChange={handleFormChange}
                    required
                    className="glass-input w-full px-4 py-2.5"
                    placeholder="Enter full vendor name"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-300">
                      Amount (USD)
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-slate-500 font-medium">$</span>
                      </div>
                      <input
                        type="number"
                        name="amount"
                        value={formData.amount}
                        onChange={handleFormChange}
                        required
                        step="0.01"
                        className="glass-input w-full pl-8 pr-4 py-2.5 font-mono"
                        placeholder="0.00"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-300">
                      Transaction Date
                    </label>
                    <input
                      type="date"
                      name="date"
                      value={formData.date}
                      onChange={handleFormChange}
                      required
                      className="glass-input w-full px-4 py-2.5 [&::-webkit-calendar-picker-indicator]:filter [&::-webkit-calendar-picker-indicator]:invert"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">
                    Department/Cost Center
                  </label>
                  <input
                    type="text"
                    name="department"
                    value={formData.department}
                    onChange={handleFormChange}
                    className="glass-input w-full px-4 py-2.5"
                    placeholder="e.g. Engineering, Marketing..."
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">
                    Description / Memo
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleFormChange}
                    rows={3}
                    className="glass-input w-full px-4 py-2.5 resize-none"
                    placeholder="Details about this transaction..."
                  />
                </div>

                <div className="pt-4 flex justify-end">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg shadow-lg shadow-blue-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-5 h-5" />
                        Commit Transaction
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Bulk Upload Component */}
          {activeTab === 'upload' && (
            <div className="glass-card rounded-2xl p-6 sm:p-10 max-w-4xl border-t border-t-white/10 text-center">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Bulk Ledger Upload</h2>
                <p className="text-slate-400 text-sm">Upload multiple transactions via CSV or Excel mapping.</p>
              </div>
              
              <div className="border-2 border-dashed border-slate-600 rounded-xl p-12 hover:border-blue-500 hover:bg-slate-800/30 transition-all cursor-pointer group">
                <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform shadow-lg">
                  <Upload className="w-10 h-10 text-blue-400" />
                </div>
                <p className="text-lg font-medium text-slate-200 mb-2 group-hover:text-white transition-colors">
                  Drag and drop your spreadsheet here
                </p>
                <p className="text-sm text-slate-400 mb-8">Supported formats: .csv, .xlsx (Max size: 50MB)</p>
                
                <input type="file" accept=".csv,.xlsx" className="hidden" id="file-upload" />
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-lg border border-slate-600 hover:border-slate-500 shadow-lg transition-all cursor-pointer"
                >
                  <Upload className="w-4 h-4" />
                  Browse Files
                </label>
              </div>
            </div>
          )}

          {/* OCR Component */}
          {activeTab === 'ocr' && (
            <div className="glass-card rounded-2xl p-6 sm:p-10 max-w-4xl border-t border-t-white/10 text-center">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Automated Document Parsing</h2>
                <p className="text-slate-400 text-sm">Upload invoices or receipts to automatically extract data fields via AI.</p>
              </div>
              
              <div className="border-2 border-dashed border-slate-600 rounded-xl p-12 hover:border-blue-500 hover:bg-slate-800/30 transition-all cursor-pointer group relative overflow-hidden">
                {/* Laser scan animation effect */}
                <div className="absolute top-0 left-0 w-full h-[2px] bg-blue-500/50 shadow-[0_0_15px_theme('colors.blue.500')] translate-y-[-100%] group-hover:animate-[slideDown_2s_ease-in-out_infinite]"></div>
                
                <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform shadow-lg relative z-10">
                  <FileText className="w-10 h-10 text-blue-400" />
                </div>
                <p className="text-lg font-medium text-slate-200 mb-2 group-hover:text-white transition-colors relative z-10">
                  Select documents for AI OCR
                </p>
                <p className="text-sm text-slate-400 mb-8 relative z-10">Supports JPG, PNG, PDF (Max 10 pages per file)</p>
                
                <input type="file" accept=".pdf,.png,.jpg,.jpeg" className="hidden" id="ocr-upload" />
                <label
                  htmlFor="ocr-upload"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 font-medium rounded-lg border border-blue-500/30 hover:border-blue-500/50 transition-all cursor-pointer relative z-10"
                >
                  <Plus className="w-4 h-4" />
                  Upload Documents
                </label>
              </div>
            </div>
          )}
        </div>
      </main>

      <style>{`
        @keyframes slideDown {
          0% { transform: translateY(-100%); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(400px); opacity: 0; }
        }
      `}</style>
    </div>
  )
}

export default FinanceDataEntry
