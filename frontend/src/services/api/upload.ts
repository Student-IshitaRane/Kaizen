import api from './auth'
import { DatasetUpload } from '../../types'

export interface UploadDatasetData {
  datasetType: 'vendor_master' | 'purchase_ledger' | 'sales_ledger' | 'general_ledger' | 'bank_transactions'
  file: File
}

export const uploadService = {
  async uploadDataset(data: UploadDatasetData): Promise<DatasetUpload> {
    const formData = new FormData()
    formData.append('dataset_type', data.datasetType)
    formData.append('file', data.file)

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getUploads(): Promise<DatasetUpload[]> {
    const response = await api.get('/upload')
    return response.data
  },

  async getUploadById(id: string): Promise<DatasetUpload> {
    const response = await api.get(`/upload/${id}`)
    return response.data
  },

  async getDatasetStatistics(datasetType: string): Promise<any> {
    const response = await api.get(`/upload/statistics/${datasetType}`)
    return response.data
  },

  async preprocessHistoricalData(datasetType: string, filePath: string, enableAnalysis?: boolean): Promise<any> {
    const response = await api.post('/upload/preprocess', {
      datasetType,
      filePath,
      enableAnalysis,
    })
    return response.data
  },
}