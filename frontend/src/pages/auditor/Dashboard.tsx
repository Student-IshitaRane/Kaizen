import { useState } from 'react'
import { format } from 'date-fns'
import { 
  Activity, 
  AlertTriangle, 
  Clock,
  TrendingUp,
  Users,
  Shield,
  Zap
} from 'lucide-react'
import KPIStatCard from '../../components/ui/KPIStatCard'
import DataTable from '../../components/ui/DataTable'
import StatusBadge from '../../components/ui/StatusBadge'
import RiskBadge from '../../components/ui/RiskBadge'
import Chart from '../../components/ui/Chart'
import useRealtimeMonitoring from '../../hooks/useRealtimeMonitoring'
import { KPI, FlaggedCase } from '../../types'

const AuditorDashboard = () => {
  const { transactions, stats, isConnected, generateMockTransaction } = useRealtimeMonitoring()
  const [kpis] = useState<KPI[]>([
    {
      title: 'Total Records Analyzed',
      value: '1,247,892',
      change: 12,
      description: 'Last 30 days',
      icon: 'trending-up',
      color: 'primary'
    },
    {
      title: 'Real-time Processed',
      value: stats.totalProcessed.toLocaleString(),
      change: 0,
      description: 'Today',
      icon: 'trending-up',
      color: 'primary'
    },
    {
      title: 'High-Risk Transactions',
      value: stats.highRiskCount.toString(),
      change: 8,
      description: 'Immediate attention',
      icon: 'trending-up',
      color: 'danger'
    },
    {
      title: 'Flagged Transactions',
      value: stats.totalFlagged.toString(),
      change: -3,
      description: 'Requiring review',
      icon: 'trending-down',
      color: 'warning'
    },
    {
      title: 'Avg Processing Time',
      value: `${stats.avgProcessingTime.toFixed(0)}ms`,
      change: -2,
      description: 'Analysis pipeline',
      icon: 'trending-down',
      color: 'primary'
    },
    {
      title: 'Pending Reviews',
      value: '312',
      change: -5,
      description: 'Awaiting auditor action',
      icon: 'trending-down',
      color: 'primary'
    }
  ])

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
      detailedExplanation: 'Amount of $12,000 is within 5% of $12,500 approval limit',
      suggestedActions: ['Verify approval chain', 'Check supporting documentation'],
      status: 'new',
      priority: 'high',
      createdAt: '2024-01-15T09:30:00Z',
      updatedAt: '2024-01-15T09:30:00Z'
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
      detailedExplanation: 'Invoice ID matches previous submission from same vendor',
      suggestedActions: ['Contact vendor', 'Review payment history'],
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
      detailedExplanation: 'Invoice dated Saturday, January 13, 2024',
      suggestedActions: ['Verify transaction date', 'Check business purpose'],
      status: 'assigned',
      priority: 'medium',
      assignedTo: 'auditor2',
      assignedUserName: 'Bob Reviewer',
      createdAt: '2024-01-13T11:45:00Z',
      updatedAt: '2024-01-14T09:30:00Z'
    }
  ]

  const recentActivity = [
    {
      id: '1',
      action: 'Confirmed Suspicious',
      caseId: 'FLG-DEF456',
      auditor: 'Alice Auditor',
      timestamp: '2024-01-15T10:15:00Z',
      details: 'Duplicate invoice confirmed as suspicious'
    },
    {
      id: '2',
      action: 'False Positive',
      caseId: 'FLG-JKL012',
      auditor: 'Bob Reviewer',
      timestamp: '2024-01-15T09:45:00Z',
      details: 'Weekend posting marked as legitimate'
    },
    {
      id: '3',
      action: 'Resolved Case',
      caseId: 'FLG-MNO345',
      auditor: 'Alice Auditor',
      timestamp: '2024-01-14T16:30:00Z',
      details: 'Threshold avoidance case resolved with documentation'
    }
  ]

  // Chart data
  const riskTrendData = [
    { name: 'Jan 8', value: 45 },
    { name: 'Jan 9', value: 52 },
    { name: 'Jan 10', value: 48 },
    { name: 'Jan 11', value: 65 },
    { name: 'Jan 12', value: 58 },
    { name: 'Jan 13', value: 72 },
    { name: 'Jan 14', value: 68 },
    { name: 'Jan 15', value: 65 }
  ]

  const vendorRiskData = [
    { name: 'Global Logistics Corp.', value: 18 },
    { name: 'Tech Supplies Inc.', value: 12 },
    { name: 'Office Solutions Ltd.', value: 8 },
    { name: 'Construction Materials Co.', value: 6 },
    { name: 'IT Services Group', value: 5 }
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
    }
  ]

  const activityColumns = [
    {
      key: 'action',
      header: 'Action',
      render: (value: string) => (
        <div className="font-medium text-gray-900">{value}</div>
      )
    },
    {
      key: 'caseId',
      header: 'Case ID',
      render: (value: string) => (
        <div className="text-gray-900 font-mono">{value}</div>
      )
    },
    {
      key: 'auditor',
      header: 'Auditor',
      render: (value: string) => (
        <div className="text-gray-900">{value}</div>
      )
    },
    {
      key: 'timestamp',
      header: 'Time',
      render: (value: string) => (
        <div className="text-sm text-gray-500">
          {format(new Date(value), 'MMM d, HH:mm')}
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Monitoring Dashboard</h1>
          <p className="mt-1 text-gray-600">
            Monitor financial risk across historical and live data
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>Last updated: {format(new Date(), 'HH:mm:ss')}</span>
          </div>
          <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border ${
            isConnected
              ? 'bg-green-50 border-green-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
            }`}></div>
            <span className={`text-sm font-medium ${
              isConnected ? 'text-green-700' : 'text-yellow-700'
            }`}>
              {isConnected ? 'Monitoring Active' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {kpis.map((kpi, index) => (
          <KPIStatCard key={index} {...kpi} />
        ))}
      </div>

      {/* Live Monitoring Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monitoring Status */}
        <div className="lg:col-span-2 glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-primary-50">
                <Activity className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Live Monitoring</h2>
                <p className="text-sm text-gray-500">Real-time transaction processing status</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-sm font-medium text-green-700">Active</span>
            </div>
          </div>

          <div className="space-y-4">
            {/* Most Recent Transaction */}
            {transactions.length > 0 ? (
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">Most Recent Transaction</p>
                  <p className="text-sm text-gray-500">
                    {transactions[0].invoiceId} • {transactions[0].vendorName}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    ${transactions[0].amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                  <p className="text-sm text-gray-500">
                    {format(new Date(transactions[0].timestamp), 'HH:mm:ss')}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">No recent transactions</p>
                  <p className="text-sm text-gray-500">Waiting for incoming data...</p>
                </div>
              </div>
            )}

            <div className="border-t border-gray-200 pt-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-900">Recent Activity</h3>
                <button
                  onClick={generateMockTransaction}
                  className="px-3 py-1 text-xs font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors flex items-center space-x-1"
                >
                  <Zap className="h-3 w-3" />
                  <span>Simulate Transaction</span>
                </button>
              </div>
              <div className="space-y-3 max-h-48 overflow-y-auto">
                {transactions.length > 0 ? (
                  transactions.map((tx, index) => (
                    <div key={index} className="flex items-center text-sm">
                      <div className={`w-2 h-2 rounded-full mr-3 ${
                        tx.status === 'flagged' ? 'bg-red-500' :
                        tx.status === 'completed' ? 'bg-green-500' :
                        'bg-blue-500'
                      }`}></div>
                      <span className="text-gray-500 mr-2">
                        {format(new Date(tx.timestamp), 'HH:mm:ss')}
                      </span>
                      <span className="text-gray-900">
                        {tx.status === 'processed' && `Transaction processed: ${tx.invoiceId}`}
                        {tx.status === 'completed' && `Analysis completed: ${tx.riskScore} (${tx.riskLevel})`}
                        {tx.status === 'flagged' && `Flagged case created: ${tx.caseId}`}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4">
                    <p className="text-sm text-gray-500">No activity yet</p>
                    <p className="text-xs text-gray-400">Transactions will appear here in real-time</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-primary-50">
              <Shield className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
              <p className="text-sm text-gray-500">Platform health and configuration</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Real-time Monitoring</span>
              <span className={`px-2 py-1 text-xs font-medium rounded ${
                isConnected 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {isConnected ? 'Connected' : 'Connecting...'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">AI Analysis Pipeline</span>
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Operational</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database Connection</span>
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Connected</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Streaming Services</span>
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">LLM Providers</span>
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">2 Available</span>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                Generate Exception Report
              </button>
              <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                View System Configuration
              </button>
              <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                Manage Alert Rules
              </button>
            </div>
          </div>
        </div>
      </div>

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
                <p className="text-sm text-gray-500">Last 7 days</p>
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

        {/* Top Risky Vendors */}
        <div className="glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-primary-50">
                <Users className="h-5 w-5 text-primary-600" />
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
      </div>

      {/* Recent Flagged Cases */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-warning-50">
              <AlertTriangle className="h-5 w-5 text-warning-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Recent Flagged Transactions</h2>
              <p className="text-sm text-gray-500">Requiring auditor review</p>
            </div>
          </div>
          <button className="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors">
            View All Cases →
          </button>
        </div>

        <DataTable
          columns={caseColumns}
          data={flaggedCases}
          emptyMessage="No flagged cases requiring review"
        />
      </div>

      {/* Recent Review Activity */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-primary-50">
              <Activity className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Recent Review Activity</h2>
              <p className="text-sm text-gray-500">Auditor actions and decisions</p>
            </div>
          </div>
        </div>

        <DataTable
          columns={activityColumns}
          data={recentActivity}
          emptyMessage="No recent review activity"
        />
      </div>
    </div>
  )
}

export default AuditorDashboard