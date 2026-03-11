import { useState, useEffect } from 'react'
import { format, subDays } from 'date-fns'
import { 
  Download, 
  Filter, 
  Calendar, 
  AlertTriangle,
  PieChart,
  TrendingUp,
  FileText,
  RefreshCw
} from 'lucide-react'
import DataTable from '../../components/ui/DataTable'
import RiskBadge from '../../components/ui/RiskBadge'
import StatusBadge from '../../components/ui/StatusBadge'
import Chart from '../../components/ui/Chart'
import { exportService } from '../../services/export'
import { FlaggedCase, FilterOptions, Pagination } from '../../types'

const ExceptionReportPage = () => {
  const [loading, setLoading] = useState(false)
  const [dateRange, setDateRange] = useState({
    startDate: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd')
  })
  const [filters, setFilters] = useState<FilterOptions>({
    riskLevel: ['high', 'medium'],
    flagType: [],
    status: ['new', 'in_review']
  })
  const [pagination] = useState<Pagination>({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  })
  const [flaggedCases] = useState<FlaggedCase[]>([])
  const [reportData, setReportData] = useState<any>(null)

  // Mock data for charts
  const riskTrendData = [
    { name: 'Jan 1', value: 45 },
    { name: 'Jan 2', value: 52 },
    { name: 'Jan 3', value: 48 },
    { name: 'Jan 4', value: 65 },
    { name: 'Jan 5', value: 58 },
    { name: 'Jan 6', value: 72 },
    { name: 'Jan 7', value: 68 }
  ]

  const flagDistributionData = [
    { name: 'Threshold Avoidance', value: 42 },
    { name: 'Duplicate Invoice', value: 28 },
    { name: 'Weekend Posting', value: 19 },
    { name: 'Round Amount', value: 15 },
    { name: 'Vendor Risk', value: 12 }
  ]

  const vendorRiskData = [
    { name: 'Global Logistics Corp.', value: 18 },
    { name: 'Tech Supplies Inc.', value: 12 },
    { name: 'Office Solutions Ltd.', value: 8 },
    { name: 'Construction Materials Co.', value: 6 },
    { name: 'IT Services Group', value: 5 }
  ]

  const loadReportData = async () => {
    setLoading(true)
    try {
      // In a real implementation, this would call the API
      // const data = await dashboardService.getExceptionReport({
      //   startDate: dateRange.startDate,
      //   endDate: dateRange.endDate,
      //   riskLevel: filters.riskLevel?.join(',')
      // })
      
      // Mock data for now
      setTimeout(() => {
        setReportData({
          summary: {
            totalCases: 1248,
            highRiskCases: 89,
            mediumRiskCases: 312,
            lowRiskCases: 847,
            averageRiskScore: 58,
            totalAmount: 12500000
          },
          trends: riskTrendData,
          distribution: flagDistributionData,
          topVendors: vendorRiskData
        })
        setLoading(false)
      }, 500)
    } catch (error) {
      console.error('Failed to load report data:', error)
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReportData()
  }, [dateRange, filters])

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
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{row.vendorId}</div>
        </div>
      )
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (value: number) => (
        <div className="font-medium text-gray-900">
          ${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      ),
      align: 'right' as const
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
      header: 'Date',
      render: (value: string) => (
        <div className="text-sm text-gray-500">
          {format(new Date(value), 'MMM d, yyyy')}
        </div>
      )
    }
  ]

  const handleExport = (format: 'csv' | 'pdf' | 'json') => {
    try {
      if (reportData) {
        exportService.exportExceptionReport(reportData, format, {
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          riskLevel: filters.riskLevel?.join(',')
        })
      } else {
        // Export mock data for demo
        const mockData = {
          summary: {
            totalCases: 1248,
            highRiskCases: 89,
            mediumRiskCases: 312,
            lowRiskCases: 847,
            averageRiskScore: 58,
            totalAmount: 12500000
          },
          cases: flaggedCases
        }
        exportService.exportExceptionReport(mockData, format, {
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          riskLevel: filters.riskLevel?.join(',')
        })
      }
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    }
  }

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Exception Report</h1>
          <p className="mt-1 text-gray-600">
            Comprehensive analysis of flagged transactions and risk patterns
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => loadReportData()}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <div className="relative">
            <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 flex items-center space-x-2">
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 hidden group-hover:block">
              <button
                onClick={() => handleExport('csv')}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-t-lg"
              >
                Export as CSV
              </button>
              <button
                onClick={() => handleExport('json')}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Export as JSON
              </button>
              <button
                onClick={() => handleExport('pdf')}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-b-lg"
              >
                Export as PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-primary-50">
              <Filter className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Report Filters</h2>
              <p className="text-sm text-gray-500">Customize your exception analysis</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4" />
                <span>Date Range</span>
              </div>
            </label>
            <div className="flex space-x-2">
              <input
                type="date"
                value={dateRange.startDate}
                onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <input
                type="date"
                value={dateRange.endDate}
                onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          {/* Risk Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Level
            </label>
            <div className="flex flex-wrap gap-2">
              {['high', 'medium', 'low'].map((level) => (
                <button
                  key={level}
                  onClick={() => {
                    const current = filters.riskLevel || []
                    const newLevels = current.includes(level as any)
                      ? current.filter(l => l !== level)
                      : [...current, level as any]
                    handleFilterChange('riskLevel', newLevels)
                  }}
                  className={`px-3 py-1.5 text-sm rounded-lg border ${
                    (filters.riskLevel || []).includes(level as any)
                      ? 'bg-red-50 border-red-200 text-red-700'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Flag Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Flag Type
            </label>
            <select
              value={filters.flagType?.[0] || ''}
              onChange={(e) => handleFilterChange('flagType', e.target.value ? [e.target.value] : [])}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Types</option>
              <option value="threshold_avoidance">Threshold Avoidance</option>
              <option value="duplicate_invoice">Duplicate Invoice</option>
              <option value="weekend_posting">Weekend Posting</option>
              <option value="round_amount">Round Amount</option>
              <option value="vendor_risk">Vendor Risk</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status?.[0] || ''}
              onChange={(e) => handleFilterChange('status', e.target.value ? [e.target.value] : [])}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Status</option>
              <option value="new">New</option>
              <option value="in_review">In Review</option>
              <option value="assigned">Assigned</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {reportData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Cases</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {reportData.summary.totalCases.toLocaleString()}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-primary-50">
                <AlertTriangle className="h-6 w-6 text-primary-600" />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                {reportData.summary.highRiskCases} high risk cases
              </p>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Amount</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  ${(reportData.summary.totalAmount / 1000000).toFixed(1)}M
                </p>
              </div>
              <div className="p-3 rounded-lg bg-green-50">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                Average risk score: {reportData.summary.averageRiskScore}
              </p>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Risk Distribution</p>
                <div className="flex items-center space-x-4 mt-1">
                  <div>
                    <p className="text-lg font-bold text-red-600">{reportData.summary.highRiskCases}</p>
                    <p className="text-xs text-gray-500">High</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-yellow-600">{reportData.summary.mediumRiskCases}</p>
                    <p className="text-xs text-gray-500">Medium</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-green-600">{reportData.summary.lowRiskCases}</p>
                    <p className="text-xs text-gray-500">Low</p>
                  </div>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-yellow-50">
                <PieChart className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Time Period</p>
                <p className="text-lg font-bold text-gray-900 mt-1">
                  {format(new Date(dateRange.startDate), 'MMM d')} - {format(new Date(dateRange.endDate), 'MMM d, yyyy')}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-blue-50">
                <Calendar className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                Last updated: {format(new Date(), 'MMM d, HH:mm')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Trend Chart */}
        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-primary-50">
                <TrendingUp className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Risk Trend</h2>
                <p className="text-sm text-gray-500">Daily average risk score</p>
              </div>
            </div>
          </div>
          <Chart
            data={riskTrendData}
            type="line"
            height={250}
            colors={['#3b82f6']}
            showGrid={true}
            showTooltip={true}
            showLegend={false}
          />
        </div>

        {/* Flag Distribution Chart */}
        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-primary-50">
                <PieChart className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Flag Distribution</h2>
                <p className="text-sm text-gray-500">By detection type</p>
              </div>
            </div>
          </div>
          <Chart
            data={flagDistributionData}
            type="pie"
            height={250}
            colors={['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']}
            showTooltip={true}
            showLegend={true}
          />
        </div>
      </div>

      {/* Top Risky Vendors */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-primary-50">
              <FileText className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Top Risky Vendors</h2>
              <p className="text-sm text-gray-500">By flagged transaction count</p>
            </div>
          </div>
        </div>
        <Chart
          data={vendorRiskData}
          type="bar"
          height={250}
          colors={['#3b82f6']}
          showGrid={true}
          showTooltip={true}
          showLegend={false}
        />
      </div>

      {/* Detailed Cases Table */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-warning-50">
              <AlertTriangle className="h-5 w-5 text-warning-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Flagged Cases</h2>
              <p className="text-sm text-gray-500">Detailed view of all flagged transactions</p>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Showing {pagination.limit} of {pagination.total} cases
          </div>
        </div>

        <DataTable
          columns={caseColumns}
          data={flaggedCases}
          emptyMessage="No flagged cases match your filters"
        />

        {/* Pagination */}
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Page {pagination.page} of {pagination.totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              disabled={pagination.page <= 1}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              disabled={pagination.page >= pagination.totalPages}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExceptionReportPage