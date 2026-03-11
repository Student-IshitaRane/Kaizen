import api from './auth'
import { KPI, ChartData } from '../../types'

export interface DashboardData {
  kpis: KPI[]
  riskTrend: ChartData[]
  flagDistribution: ChartData[]
  topRiskyVendors: ChartData[]
  recentFlaggedCases: any[]
  recentActivity: any[]
  monitoringStatus: {
    active: boolean
    lastUpdated: string
    recentTransaction?: any
  }
}

export const dashboardService = {
  async getAuditorDashboard(): Promise<DashboardData> {
    const response = await api.get('/dashboard/auditor')
    return response.data
  },

  async getFinanceDashboard(): Promise<any> {
    const response = await api.get('/dashboard/finance')
    return response.data
  },

  async getSystemInfo(): Promise<any> {
    const response = await api.get('/system-info')
    return response.data
  },

  async getExceptionReport(params?: {
    startDate?: string
    endDate?: string
    riskLevel?: string
  }): Promise<any> {
    const response = await api.get('/reports/exception', { params })
    return response.data
  },
}