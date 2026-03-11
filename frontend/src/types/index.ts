export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'finance' | 'auditor' | 'admin'
  department?: string
  avatar?: string
}

export interface Transaction {
  id: string
  invoiceId: string
  vendorId: string
  vendorName?: string
  amount: number
  currency: string
  invoiceDate: string
  postingDate?: string
  department: string
  description?: string
  approverId?: string
  status: 'submitted' | 'approved' | 'rejected' | 'flagged'
  createdAt: string
  analysisSummary?: AnalysisSummary
}

export interface AnalysisSummary {
  pipelineStatus: string
  processingTimeMs: number
  riskScore: number
  riskLevel: 'low' | 'medium' | 'high'
  flaggedCaseCreated: boolean
  flaggedCaseId?: string
}

export interface FlaggedCase {
  id: string
  caseId: string
  transactionId: string
  transactionRefId: string
  vendorId: string
  vendorName?: string
  amount: number
  flagType: string
  riskScore: number
  riskLevel: 'low' | 'medium' | 'high'
  reasonSummary: string
  detailedExplanation: string
  suggestedActions: string[]
  status: 'new' | 'in_review' | 'assigned' | 'resolved' | 'dismissed'
  priority: 'low' | 'medium' | 'high'
  assignedTo?: string
  assignedUserName?: string
  reviewNotes?: string
  resolution?: string
  resolvedAt?: string
  createdAt: string
  updatedAt: string
  analysisMetadata?: Record<string, any>
}

export interface DatasetUpload {
  id: string
  datasetType: 'vendor_master' | 'purchase_ledger' | 'sales_ledger' | 'general_ledger' | 'bank_transactions'
  fileName: string
  uploadDate: string
  recordsImported: number
  status: 'uploaded' | 'validating' | 'standardized' | 'stored' | 'failed'
  errorMessage?: string
}

export interface KPI {
  title: string
  value: number | string
  change?: number
  description: string
  icon: string
  color: 'primary' | 'success' | 'warning' | 'danger' | 'gray'
}

export interface ChartData {
  name: string
  value: number
}

export interface FilterOptions {
  riskLevel?: ('low' | 'medium' | 'high')[]
  flagType?: string[]
  status?: string[]
  vendor?: string
  dateFrom?: string
  dateTo?: string
  search?: string
}

export interface Pagination {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
  error?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  token: string
}