import { useState } from 'react'
import { format } from 'date-fns'
import { 
  Upload, 
  CheckCircle, 
  AlertCircle,
  DollarSign,
  Calendar,
  Building,
  User
} from 'lucide-react'
import DataTable from '../../components/ui/DataTable'
import StatusBadge from '../../components/ui/StatusBadge'
import RiskBadge from '../../components/ui/RiskBadge'
import { Transaction } from '../../types'
import toast from 'react-hot-toast'

const FinanceDashboard = () => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showResult, setShowResult] = useState(false)
  const [formData, setFormData] = useState({
    vendorId: '',
    invoiceId: '',
    amount: '',
    invoiceDate: format(new Date(), 'yyyy-MM-dd'),
    department: '',
    approverId: '',
    description: '',
    transactionType: 'purchase'
  })

  // Mock data for recent transactions
  const recentTransactions: Transaction[] = [
    {
      id: '1',
      invoiceId: 'INV-2024-1001',
      vendorId: 'VEND001',
      vendorName: 'Tech Supplies Inc.',
      amount: 9999.99,
      currency: 'USD',
      invoiceDate: '2024-01-15',
      department: 'IT',
      description: 'Software license renewal',
      status: 'submitted',
      createdAt: '2024-01-15T10:30:00Z',
      analysisSummary: {
        pipelineStatus: 'success',
        processingTimeMs: 1200,
        riskScore: 25,
        riskLevel: 'low',
        flaggedCaseCreated: false
      }
    },
    {
      id: '2',
      invoiceId: 'INV-2024-1002',
      vendorId: 'VEND002',
      vendorName: 'Office Solutions Ltd.',
      amount: 4500.00,
      currency: 'USD',
      invoiceDate: '2024-01-14',
      department: 'Operations',
      description: 'Office furniture',
      status: 'approved',
      createdAt: '2024-01-14T14:20:00Z'
    },
    {
      id: '3',
      invoiceId: 'INV-2024-1003',
      vendorId: 'VEND003',
      vendorName: 'Global Logistics Corp.',
      amount: 12000.00,
      currency: 'USD',
      invoiceDate: '2024-01-13',
      department: 'Logistics',
      description: 'Shipping services',
      status: 'flagged',
      createdAt: '2024-01-13T09:15:00Z',
      analysisSummary: {
        pipelineStatus: 'success',
        processingTimeMs: 1800,
        riskScore: 65,
        riskLevel: 'medium',
        flaggedCaseCreated: true,
        flaggedCaseId: 'FLG-ABC123'
      }
    }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false)
      setShowResult(true)
      toast.success('Transaction submitted successfully')
      
      // Reset form
      setFormData({
        vendorId: '',
        invoiceId: '',
        amount: '',
        invoiceDate: format(new Date(), 'yyyy-MM-dd'),
        department: '',
        approverId: '',
        description: '',
        transactionType: 'purchase'
      })
    }, 1500)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const transactionColumns = [
    {
      key: 'invoiceId',
      header: 'Invoice ID',
      render: (value: string) => (
        <div className="font-medium text-gray-900">{value}</div>
      )
    },
    {
      key: 'vendorName',
      header: 'Vendor',
      render: (value: string, row: Transaction) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{row.vendorId}</div>
        </div>
      )
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (value: number, row: Transaction) => (
        <div className="text-right">
          <div className="font-medium text-gray-900">
            ${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-gray-500">{row.currency}</div>
        </div>
      ),
      align: 'right' as const
    },
    {
      key: 'invoiceDate',
      header: 'Date',
      render: (value: string) => (
        <div className="text-gray-900">{format(new Date(value), 'MMM d, yyyy')}</div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string, row: Transaction) => (
        <div className="flex items-center space-x-2">
          <StatusBadge status={value} size="sm" />
          {row.analysisSummary && (
            <RiskBadge level={row.analysisSummary.riskLevel} size="sm" />
          )}
        </div>
      )
    },
    {
      key: 'createdAt',
      header: 'Submitted',
      render: (value: string) => (
        <div className="text-sm text-gray-500">
          {format(new Date(value), 'HH:mm')}
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Real-Time Transaction Entry</h1>
          <p className="mt-1 text-gray-600">
            Submit financial transactions for continuous audit monitoring
          </p>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-50 rounded-lg border border-green-200">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-sm font-medium text-green-700">Real-time mode active</span>
        </div>
      </div>

      {/* Transaction Form */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 rounded-lg bg-primary-50">
            <Upload className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">New Transaction</h2>
            <p className="text-sm text-gray-500">Enter transaction details for audit monitoring</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Vendor Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Vendor ID <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Building className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    name="vendorId"
                    value={formData.vendorId}
                    onChange={handleChange}
                    required
                    className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="VEND001"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Invoice ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="invoiceId"
                  value={formData.invoiceId}
                  onChange={handleChange}
                  required
                  className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="INV-2024-XXXX"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <DollarSign className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    required
                    step="0.01"
                    min="0"
                    className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>

            {/* Transaction Details */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Invoice Date <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Calendar className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="date"
                    name="invoiceDate"
                    value={formData.invoiceDate}
                    onChange={handleChange}
                    required
                    className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <select
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select department</option>
                  <option value="IT">IT</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Operations">Operations</option>
                  <option value="Finance">Finance</option>
                  <option value="HR">HR</option>
                  <option value="Logistics">Logistics</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Approver ID
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    name="approverId"
                    value={formData.approverId}
                    onChange={handleChange}
                    className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="APPR001"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Enter transaction description..."
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <Upload className="h-5 w-5 mr-2" />
                  Submit for Audit
                </>
              )}
            </button>
          </div>
        </form>

        {/* Submission Result */}
        {showResult && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200 animate-fade-in">
            <div className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 mr-3" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-green-800">Transaction Submitted Successfully</h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>Transaction has been submitted for real-time audit analysis.</p>
                  <div className="mt-2 grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-medium">Reference:</span> INV-2024-1004
                    </div>
                    <div>
                      <span className="font-medium">Status:</span> Sent for analysis
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recent Transactions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Submissions</h2>
          <span className="text-sm text-gray-500">Newest transactions appear first</span>
        </div>
        
        <DataTable
          columns={transactionColumns}
          data={recentTransactions}
          emptyMessage="No transactions submitted yet"
        />
        
        <div className="mt-4 flex items-center text-sm text-gray-500">
          <AlertCircle className="h-4 w-4 mr-2" />
          <span>Transactions are analyzed in real-time. Flagged items appear in auditor dashboard.</span>
        </div>
      </div>
    </div>
  )
}

export default FinanceDashboard