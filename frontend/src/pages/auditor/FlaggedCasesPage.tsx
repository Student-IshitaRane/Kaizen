import { useState } from 'react'
import { format } from 'date-fns'
import { 
  Search, 
  Filter, 
  ChevronDown, 
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  FileText,
  Building,
  DollarSign
} from 'lucide-react'
import DataTable from '../../components/ui/DataTable'
import StatusBadge from '../../components/ui/StatusBadge'
import RiskBadge from '../../components/ui/RiskBadge'
import { FlaggedCase } from '../../types'

const FlaggedCasesPage = () => {
  const [selectedCase, setSelectedCase] = useState<FlaggedCase | null>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [filters, setFilters] = useState({
    riskLevel: [] as string[],
    flagType: [] as string[],
    status: [] as string[],
    vendor: '',
    dateFrom: '',
    dateTo: '',
    search: ''
  })

  // Mock data for flagged cases
  const flaggedCases: FlaggedCase[] = [
    {
      id: '1',
      caseId: 'FLG-ABC123',
      transactionId: '1',
      transactionRefId: 'INV-2024-1003',
      vendorId: 'VEND003',
      vendorName: 'Global Logistics Corp.',
      amount: 12000.00,
      flagType: 'threshold_avoidance',
      riskScore: 65,
      riskLevel: 'medium',
      reasonSummary: 'Transaction amount just below approval threshold',
      detailedExplanation: 'Amount of $12,000 is within 5% of $12,500 approval limit. This pattern may indicate intentional avoidance of higher approval requirements.',
      suggestedActions: [
        'Verify approval chain and authority',
        'Check supporting documentation for business purpose',
        'Review previous transactions with same vendor',
        'Confirm goods/services were received'
      ],
      status: 'new',
      priority: 'high',
      createdAt: '2024-01-15T09:30:00Z',
      updatedAt: '2024-01-15T09:30:00Z',
      analysisMetadata: {
        scoring_breakdown: {
          anomaly_scores: [
            { type: 'threshold_avoidance', score: 25, severity: 'medium' },
            { type: 'round_number_amount', score: 15, severity: 'low' }
          ],
          pattern_scores: [
            { type: 'vendor_payment_spike', score: 15, severity: 'medium' }
          ],
          validation_scores: []
        }
      }
    },
    {
      id: '2',
      caseId: 'FLG-DEF456',
      transactionId: '2',
      transactionRefId: 'INV-2024-0998',
      vendorId: 'VEND001',
      vendorName: 'Tech Supplies Inc.',
      amount: 9999.99,
      flagType: 'exact_duplicate',
      riskScore: 85,
      riskLevel: 'high',
      reasonSummary: 'Exact duplicate invoice detected',
      detailedExplanation: 'Invoice ID matches previous submission from same vendor within last 30 days. Same amount and date suggest potential duplicate payment.',
      suggestedActions: [
        'Contact vendor to confirm invoice validity',
        'Review payment history for duplicate payments',
        'Check purchase order and receiving documentation',
        'Investigate if this is a legitimate duplicate'
      ],
      status: 'in_review',
      priority: 'high',
      assignedTo: 'auditor1',
      assignedUserName: 'Alice Auditor',
      createdAt: '2024-01-14T14:20:00Z',
      updatedAt: '2024-01-15T10:15:00Z'
    },
    {
      id: '3',
      caseId: 'FLG-GHI789',
      transactionId: '3',
      transactionRefId: 'INV-2024-1001',
      vendorId: 'VEND002',
      vendorName: 'Office Solutions Ltd.',
      amount: 2500.00,
      flagType: 'weekend_posting',
      riskScore: 45,
      riskLevel: 'medium',
      reasonSummary: 'Transaction posted on weekend',
      detailedExplanation: 'Invoice dated Saturday, January 13, 2024. Weekend transactions are unusual for this vendor and department.',
      suggestedActions: [
        'Verify transaction date with business unit',
        'Check if weekend service was required',
        'Review authorization for weekend posting',
        'Confirm business purpose documentation'
      ],
      status: 'assigned',
      priority: 'medium',
      assignedTo: 'auditor2',
      assignedUserName: 'Bob Reviewer',
      createdAt: '2024-01-13T11:45:00Z',
      updatedAt: '2024-01-14T09:30:00Z'
    },
    {
      id: '4',
      caseId: 'FLG-JKL012',
      transactionId: '4',
      transactionRefId: 'INV-2024-0995',
      vendorId: 'VEND004',
      vendorName: 'Dormant Vendor LLC',
      amount: 5000.00,
      flagType: 'dormant_vendor',
      riskScore: 75,
      riskLevel: 'high',
      reasonSummary: 'Dormant vendor reactivated after 180 days',
      detailedExplanation: 'Vendor was inactive for 180+ days before this transaction. Reactivation of dormant vendors requires additional verification.',
      suggestedActions: [
        'Verify vendor registration is still valid',
        'Check updated vendor information',
        'Review reason for reactivation',
        'Confirm business relationship renewal'
      ],
      status: 'new',
      priority: 'high',
      createdAt: '2024-01-12T16:30:00Z',
      updatedAt: '2024-01-12T16:30:00Z'
    }
  ]

  const caseColumns = [
    {
      key: 'transactionRefId',
      header: 'Transaction ID',
      render: (value: string, row: FlaggedCase) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{row.caseId}</div>
        </div>
      )
    },
    {
      key: 'vendorName',
      header: 'Vendor',
      render: (value: string, row: FlaggedCase) => (
        <div className="flex items-center">
          <Building className="h-4 w-4 text-gray-400 mr-2" />
          <div>
            <div className="font-medium text-gray-900">{value}</div>
            <div className="text-sm text-gray-500">{row.vendorId}</div>
          </div>
        </div>
      )
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (value: number) => (
        <div className="flex items-center">
          <DollarSign className="h-4 w-4 text-gray-400 mr-2" />
          <div className="font-medium text-gray-900">
            ${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>
      )
    },
    {
      key: 'flagType',
      header: 'Flag Type',
      render: (value: string) => (
        <div className="capitalize text-gray-900">
          {value.replace('_', ' ')}
        </div>
      )
    },
    {
      key: 'riskScore',
      header: 'Risk',
      render: (value: number, row: FlaggedCase) => (
        <RiskBadge level={row.riskLevel} score={value} showScore />
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string, row: FlaggedCase) => (
        <div className="flex items-center space-x-2">
          <StatusBadge status={value} size="sm" />
          {row.priority === 'high' && (
            <span className="px-1.5 py-0.5 text-xs font-medium bg-red-100 text-red-800 rounded">
              High Priority
            </span>
          )}
        </div>
      )
    },
    {
      key: 'createdAt',
      header: 'Flagged',
      render: (value: string) => (
        <div className="text-sm text-gray-500">
          {format(new Date(value), 'MMM d, HH:mm')}
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (_: any, row: FlaggedCase) => (
        <button
          onClick={() => {
            setSelectedCase(row)
            setIsDetailOpen(true)
          }}
          className="px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors flex items-center"
        >
          <Eye className="h-4 w-4 mr-1" />
          Review
        </button>
      )
    }
  ]

  const handleFilterChange = (key: keyof typeof filters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleReviewDecision = (decision: string) => {
    if (!selectedCase) return
    
    // In a real app, this would call an API
    console.log(`Review decision for ${selectedCase.caseId}: ${decision}`)
    setIsDetailOpen(false)
    setSelectedCase(null)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Flagged Transactions & Case Review</h1>
          <p className="mt-1 text-gray-600">
            Review and investigate flagged transactions with detailed risk analysis
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            <span className="font-medium text-gray-900">{flaggedCases.length}</span> cases requiring review
          </div>
          <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors">
            Export Report
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card rounded-xl p-4">
        <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Search by transaction ID, vendor, or case ID..."
              />
            </div>
          </div>

          {/* Quick Filters */}
          <div className="flex items-center space-x-2">
            <button className="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg border border-gray-300 flex items-center">
              <Filter className="h-4 w-4 mr-2" />
              Filters
              <ChevronDown className="h-4 w-4 ml-1" />
            </button>
            
            <select
              value={filters.riskLevel.join(',')}
              onChange={(e) => handleFilterChange('riskLevel', e.target.value ? e.target.value.split(',') : [])}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Risk Levels</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>

            <select
              value={filters.status.join(',')}
              onChange={(e) => handleFilterChange('status', e.target.value ? e.target.value.split(',') : [])}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="new">New</option>
              <option value="in_review">In Review</option>
              <option value="assigned">Assigned</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>

        {/* Date Range */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date From
            </label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date To
            </label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => handleFilterChange('dateTo', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vendor
            </label>
            <input
              type="text"
              value={filters.vendor}
              onChange={(e) => handleFilterChange('vendor', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Vendor ID or name..."
            />
          </div>
        </div>
      </div>

      {/* Main Cases Table */}
      <DataTable
        columns={caseColumns}
        data={flaggedCases}
        emptyMessage="No flagged cases match your filters"
      />

      {/* Case Detail Drawer */}
      {isDetailOpen && selectedCase && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setIsDetailOpen(false)}></div>
          
          <div className="fixed inset-y-0 right-0 pl-10 max-w-full flex">
            <div className="relative w-screen max-w-4xl">
              <div className="h-full flex flex-col bg-white shadow-xl overflow-y-auto">
                {/* Header */}
                <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
                  <div className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900">Case Review: {selectedCase.caseId}</h2>
                        <p className="text-sm text-gray-500">Transaction: {selectedCase.transactionRefId}</p>
                      </div>
                      <div className="flex items-center space-x-4">
                        <RiskBadge level={selectedCase.riskLevel} score={selectedCase.riskScore} showScore />
                        <button
                          onClick={() => setIsDetailOpen(false)}
                          className="text-gray-400 hover:text-gray-500"
                        >
                          <span className="sr-only">Close</span>
                          <XCircle className="h-6 w-6" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 px-6 py-4 space-y-6">
                  {/* Transaction Summary */}
                  <div className="glass-card rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Transaction Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">Vendor</p>
                        <p className="font-medium text-gray-900">{selectedCase.vendorName}</p>
                        <p className="text-sm text-gray-500">{selectedCase.vendorId}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Amount</p>
                        <p className="font-medium text-gray-900">
                          ${selectedCase.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Flag Type</p>
                        <p className="font-medium text-gray-900 capitalize">
                          {selectedCase.flagType.replace('_', ' ')}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Flagged</p>
                        <p className="font-medium text-gray-900">
                          {format(new Date(selectedCase.createdAt), 'MMM d, yyyy')}
                        </p>
                        <p className="text-sm text-gray-500">
                          {format(new Date(selectedCase.createdAt), 'HH:mm')}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Why Flagged */}
                  <div className="glass-card rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <AlertTriangle className="h-5 w-5 text-warning-500" />
                      <h3 className="text-sm font-medium text-gray-900">Why Flagged</h3>
                    </div>
                    <p className="text-gray-700 mb-3">{selectedCase.reasonSummary}</p>
                    <p className="text-sm text-gray-600">{selectedCase.detailedExplanation}</p>
                  </div>

                  {/* Suggested Audit Actions */}
                  <div className="glass-card rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Suggested Audit Actions</h3>
                    <ul className="space-y-2">
                      {selectedCase.suggestedActions.map((action, index) => (
                        <li key={index} className="flex items-start">
                          <FileText className="h-4 w-4 text-primary-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Review Decision Panel */}
                  <div className="glass-card rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-4">Review Decision</h3>
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={() => handleReviewDecision('confirmed_suspicious')}
                          className="px-4 py-3 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors flex items-center justify-center"
                        >
                          <AlertTriangle className="h-4 w-4 mr-2" />
                          Confirmed Suspicious
                        </button>
                        <button
                          onClick={() => handleReviewDecision('false_positive')}
                          className="px-4 py-3 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors flex items-center justify-center"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          False Positive
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={() => handleReviewDecision('needs_review')}
                          className="px-4 py-3 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors flex items-center justify-center"
                        >
                          <Clock className="h-4 w-4 mr-2" />
                          Needs More Review
                        </button>
                        <button
                          onClick={() => handleReviewDecision('resolved')}
                          className="px-4 py-3 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors flex items-center justify-center"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Resolved
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FlaggedCasesPage