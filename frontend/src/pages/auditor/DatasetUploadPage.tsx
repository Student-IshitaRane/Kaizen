import { useState } from 'react'
import { format } from 'date-fns'
import { Upload, FileText, Database, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import DataTable from '../../components/ui/DataTable'
import StatusBadge from '../../components/ui/StatusBadge'
import { DatasetUpload } from '../../types'
import toast from 'react-hot-toast'

const DatasetUploadPage = () => {
  const [selectedDatasetType, setSelectedDatasetType] = useState('vendor_master')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const datasetTypes = [
    { value: 'vendor_master', label: 'Vendor Master', description: 'Vendor information and details' },
    { value: 'purchase_ledger', label: 'Purchase Ledger', description: 'Purchase transactions and invoices' },
    { value: 'sales_ledger', label: 'Sales Ledger', description: 'Sales transactions and revenue' },
    { value: 'general_ledger', label: 'General Ledger', description: 'General accounting entries' },
    { value: 'bank_transactions', label: 'Bank Transactions', description: 'Bank statements and transactions' },
  ]

  // Mock data for uploaded datasets
  const uploadedDatasets: DatasetUpload[] = [
    {
      id: '1',
      datasetType: 'purchase_ledger',
      fileName: 'purchase_ledger_2024_q1.csv',
      uploadDate: '2024-01-15T10:30:00Z',
      recordsImported: 12478,
      status: 'stored'
    },
    {
      id: '2',
      datasetType: 'vendor_master',
      fileName: 'vendor_master_2024.csv',
      uploadDate: '2024-01-14T14:20:00Z',
      recordsImported: 2456,
      status: 'stored'
    },
    {
      id: '3',
      datasetType: 'bank_transactions',
      fileName: 'bank_statements_2023_q4.xlsx',
      uploadDate: '2024-01-13T09:15:00Z',
      recordsImported: 89234,
      status: 'standardized'
    },
    {
      id: '4',
      datasetType: 'general_ledger',
      fileName: 'gl_entries_2023.csv',
      uploadDate: '2024-01-12T16:45:00Z',
      recordsImported: 0,
      status: 'failed',
      errorMessage: 'Invalid date format in column "entry_date"'
    }
  ]

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file to upload')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsUploading(false)
          toast.success('Dataset uploaded successfully')
          setSelectedFile(null)
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    const file = e.dataTransfer.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const datasetColumns = [
    {
      key: 'datasetType',
      header: 'Dataset Type',
      render: (value: string) => (
        <div className="flex items-center">
          <Database className="h-4 w-4 text-gray-400 mr-2" />
          <div>
            <div className="font-medium text-gray-900 capitalize">
              {value.replace('_', ' ')}
            </div>
          </div>
        </div>
      )
    },
    {
      key: 'fileName',
      header: 'File Name',
      render: (value: string) => (
        <div className="font-medium text-gray-900">{value}</div>
      )
    },
    {
      key: 'uploadDate',
      header: 'Upload Date',
      render: (value: string) => (
        <div className="text-gray-900">
          {format(new Date(value), 'MMM d, yyyy')}
          <div className="text-sm text-gray-500">
            {format(new Date(value), 'HH:mm')}
          </div>
        </div>
      )
    },
    {
      key: 'recordsImported',
      header: 'Records',
      render: (value: number) => (
        <div className="text-right">
          <div className="font-medium text-gray-900">
            {value.toLocaleString()}
          </div>
          <div className="text-sm text-gray-500">records</div>
        </div>
      ),
      align: 'right' as const
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string, row: DatasetUpload) => (
        <div className="flex items-center space-x-2">
          <StatusBadge status={value} size="sm" />
          {row.errorMessage && (
            <div className="text-xs text-red-600" title={row.errorMessage}>
              <AlertCircle className="h-3 w-3" />
            </div>
          )}
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      render: () => (
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded transition-colors">
            View
          </button>
          <button className="px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded transition-colors">
            Reprocess
          </button>
        </div>
      )
    }
  ]

  const selectedDataset = datasetTypes.find(ds => ds.value === selectedDatasetType)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Historical Dataset Upload</h1>
          <p className="mt-1 text-gray-600">
            Upload and process historical financial datasets for audit analysis
          </p>
        </div>
      </div>

      {/* Upload Card */}
      <div className="glass-card rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 rounded-lg bg-primary-50">
            <Upload className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Upload Dataset</h2>
            <p className="text-sm text-gray-500">Select dataset type and upload file for processing</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Form */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dataset Type <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedDatasetType}
                onChange={(e) => setSelectedDatasetType(e.target.value)}
                className="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {datasetTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              {selectedDataset && (
                <p className="mt-2 text-sm text-gray-500">{selectedDataset.description}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                File <span className="text-red-500">*</span>
              </label>
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  selectedFile 
                    ? 'border-primary-300 bg-primary-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {selectedFile ? (
                  <div className="space-y-3">
                    <FileText className="h-12 w-12 text-primary-500 mx-auto" />
                    <div>
                      <p className="font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                    <div>
                      <p className="font-medium text-gray-900">Drag and drop your file here</p>
                      <p className="text-sm text-gray-500">or click to browse</p>
                    </div>
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      onChange={handleFileSelect}
                      accept=".csv,.xlsx,.xls"
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 cursor-pointer"
                    >
                      Browse Files
                    </label>
                  </div>
                )}
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Supported formats: CSV, Excel (.xlsx, .xls). Max file size: 100MB
              </p>
            </div>

            {/* Upload Progress */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-700">Uploading...</span>
                  <span className="font-medium text-gray-900">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Upload Button */}
            <div className="pt-4">
              <button
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                className="w-full flex justify-center items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5 mr-2" />
                    Upload and Process Dataset
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Ingestion Pipeline */}
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-4">Ingestion Pipeline Status</h3>
              <div className="space-y-4">
                {[
                  { stage: 'Uploaded', status: 'pending', description: 'File received and validated' },
                  { stage: 'Validating', status: 'pending', description: 'Checking data format and structure' },
                  { stage: 'Standardized', status: 'pending', description: 'Normalizing data fields and formats' },
                  { stage: 'Stored', status: 'pending', description: 'Persisting to audit database' },
                ].map((step, index) => (
                  <div key={index} className="flex items-start">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      step.status === 'completed' 
                        ? 'bg-green-100 text-green-600' 
                        : step.status === 'active'
                        ? 'bg-primary-100 text-primary-600'
                        : 'bg-gray-100 text-gray-400'
                    }`}>
                      {step.status === 'completed' ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : step.status === 'active' ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current"></div>
                      ) : (
                        <Clock className="h-5 w-5" />
                      )}
                    </div>
                    <div className="ml-4">
                      <p className={`text-sm font-medium ${
                        step.status === 'completed' 
                          ? 'text-green-700' 
                          : step.status === 'active'
                          ? 'text-primary-700'
                          : 'text-gray-700'
                      }`}>
                        {step.stage}
                      </p>
                      <p className="text-sm text-gray-500">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-sm font-medium text-gray-900 mb-4">Dataset Requirements</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>CSV files should use UTF-8 encoding</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Include header row with column names</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Dates in YYYY-MM-DD format</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Amounts as numbers (no currency symbols)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Dataset Summary */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Uploaded Dataset Summary</h2>
            <p className="text-sm text-gray-500">Previously uploaded and processed datasets</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Total: {uploadedDatasets.length} datasets</span>
            <button className="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors">
              Refresh
            </button>
          </div>
        </div>
        
        <DataTable
          columns={datasetColumns}
          data={uploadedDatasets}
          emptyMessage="No datasets uploaded yet"
        />
      </div>
    </div>
  )
}

export default DatasetUploadPage