import { saveAs } from 'file-saver'
import { FlaggedCase } from '../types'

export interface ExportOptions {
  format: 'csv' | 'json' | 'pdf'
  includeHeaders?: boolean
  filename?: string
  data: any[]
}

class ExportService {
  exportToCSV(data: any[], filename: string = 'export.csv') {
    if (data.length === 0) {
      throw new Error('No data to export')
    }

    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header]
          // Handle special characters and wrap in quotes if needed
          if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return value
        }).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, filename)
  }

  exportToJSON(data: any[], filename: string = 'export.json') {
    const jsonContent = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
    saveAs(blob, filename)
  }

  exportFlaggedCases(cases: FlaggedCase[], format: 'csv' | 'json' | 'pdf', options?: {
    startDate?: string
    endDate?: string
    riskLevel?: string
  }) {
    const formattedData = cases.map(caseItem => ({
      'Case ID': caseItem.caseId,
      'Transaction ID': caseItem.transactionRefId,
      'Vendor ID': caseItem.vendorId,
      'Vendor Name': caseItem.vendorName,
      'Amount': `$${caseItem.amount.toFixed(2)}`,
      'Flag Type': caseItem.flagType.replace('_', ' '),
      'Risk Score': caseItem.riskScore,
      'Risk Level': caseItem.riskLevel,
      'Status': caseItem.status,
      'Priority': caseItem.priority,
      'Created At': new Date(caseItem.createdAt).toLocaleString(),
      'Updated At': new Date(caseItem.updatedAt).toLocaleString(),
      'Reason Summary': caseItem.reasonSummary,
      'Detailed Explanation': caseItem.detailedExplanation,
      'Suggested Actions': caseItem.suggestedActions?.join('; ') || ''
    }))

    const dateRange = options?.startDate && options?.endDate 
      ? `${options.startDate}_to_${options.endDate}`
      : 'all_dates'

    const riskFilter = options?.riskLevel ? `_${options.riskLevel}_risk` : ''

    const filename = `flagged_cases_${dateRange}${riskFilter}_${new Date().toISOString().split('T')[0]}`

    switch (format) {
      case 'csv':
        this.exportToCSV(formattedData, `${filename}.csv`)
        break
      case 'json':
        this.exportToJSON(cases, `${filename}.json`)
        break
      case 'pdf':
        this.exportToPDF(formattedData)
        break
    }
  }

  exportToPDF(data: any[]) {
    // In a real implementation, this would generate a PDF using a library like jsPDF
    // For now, we'll create a simple HTML table and use browser print functionality
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Export Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { color: #333; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; font-weight: bold; }
          tr:nth-child(even) { background-color: #f9f9f9; }
          .header { display: flex; justify-content: space-between; margin-bottom: 20px; }
          .timestamp { color: #666; font-size: 12px; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>Audit Analytics Report</h1>
          <div class="timestamp">Generated: ${new Date().toLocaleString()}</div>
        </div>
        <table>
          <thead>
            <tr>
              ${Object.keys(data[0] || {}).map(key => `<th>${key}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${data.map(row => `
              <tr>
                ${Object.values(row).map(value => `<td>${value}</td>`).join('')}
              </tr>
            `).join('')}
          </tbody>
        </table>
      </body>
      </html>
    `

    const blob = new Blob([html], { type: 'text/html;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const printWindow = window.open(url, '_blank')
    
    if (printWindow) {
      printWindow.onload = () => {
        printWindow.print()
        printWindow.onafterprint = () => {
          URL.revokeObjectURL(url)
          printWindow.close()
        }
      }
    }
  }

  exportExceptionReport(data: any, format: 'csv' | 'json' | 'pdf', options?: {
    startDate?: string
    endDate?: string
    riskLevel?: string
  }) {
    const reportData = {
      summary: data.summary,
      filters: options,
      generatedAt: new Date().toISOString(),
      data: data.cases || []
    }

    const dateRange = options?.startDate && options?.endDate 
      ? `${options.startDate}_to_${options.endDate}`
      : 'all_dates'

    const filename = `exception_report_${dateRange}_${new Date().toISOString().split('T')[0]}`

    switch (format) {
      case 'csv':
        if (data.cases && data.cases.length > 0) {
          this.exportFlaggedCases(data.cases, 'csv', options)
        } else {
          this.exportToCSV([reportData.summary], `${filename}.csv`)
        }
        break
      case 'json':
        this.exportToJSON([reportData], `${filename}.json`)
        break
      case 'pdf':
        this.exportToPDF([reportData.summary])
        break
    }
  }
}

export const exportService = new ExportService()