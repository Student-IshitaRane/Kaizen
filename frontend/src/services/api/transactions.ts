import api from './auth'
import { Transaction, AnalysisSummary } from '../../types'

export interface CreateTransactionData {
  invoiceId: string
  vendorId: string
  amount: number
  invoiceDate: string
  department?: string
  approverId?: string
  description?: string
  currency?: string
  postingDate?: string
  costCenter?: string
  glAccount?: string
  referenceNumber?: string
  poNumber?: string
  paymentMethod?: string
  bankAccount?: string
}

export interface TransactionListResponse {
  transactions: Transaction[]
  total: number
  page: number
  limit: number
}

export const transactionService = {
  async createTransaction(data: CreateTransactionData): Promise<Transaction & { analysisSummary?: AnalysisSummary }> {
    const response = await api.post('/transactions', data)
    return response.data
  },

  async getTransactions(params?: {
    page?: number
    limit?: number
    startDate?: string
    endDate?: string
    vendorId?: string
    minAmount?: number
    maxAmount?: number
    department?: string
  }): Promise<TransactionListResponse> {
    const response = await api.get('/transactions', { params })
    return response.data
  },

  async getTransactionById(id: string): Promise<Transaction> {
    const response = await api.get(`/transactions/${id}`)
    return response.data
  },

  async getVendorSummary(vendorId: string): Promise<any> {
    const response = await api.get(`/transactions/vendor/${vendorId}/summary`)
    return response.data
  },
}