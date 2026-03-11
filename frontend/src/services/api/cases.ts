import api from './auth'
import { FlaggedCase } from '../../types'

export interface CaseListResponse {
  cases: FlaggedCase[]
  total: number
  page: number
  limit: number
}

export interface CaseReviewData {
  status: 'new' | 'in_review' | 'assigned' | 'resolved' | 'dismissed'
  notes?: string
  actionTaken?: string
}

export interface CaseAssignData {
  auditorId: string
}

export const caseService = {
  async getCases(params?: {
    page?: number
    limit?: number
    status?: string
    riskLevel?: string
    priority?: string
    flagType?: string
    vendorId?: string
    assignedTo?: string
    dateFrom?: string
    dateTo?: string
  }): Promise<CaseListResponse> {
    const response = await api.get('/cases', { params })
    return response.data
  },

  async getCaseById(id: string): Promise<FlaggedCase> {
    const response = await api.get(`/cases/${id}`)
    return response.data
  },

  async getCaseAnalysisDetails(id: string): Promise<any> {
    const response = await api.get(`/cases/${id}/analysis`)
    return response.data
  },

  async reviewCase(id: string, data: CaseReviewData): Promise<FlaggedCase> {
    const response = await api.put(`/cases/${id}/review`, data)
    return response.data
  },

  async assignCase(id: string, data: CaseAssignData): Promise<FlaggedCase> {
    const response = await api.post(`/cases/${id}/assign`, data)
    return response.data
  },

  async updateCaseStatus(id: string, status: string, notes?: string): Promise<FlaggedCase> {
    const response = await api.patch(`/cases/${id}/status`, { status, notes })
    return response.data
  },
}