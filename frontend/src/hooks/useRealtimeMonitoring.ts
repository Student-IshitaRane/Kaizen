import { useState, useEffect, useCallback } from 'react'
import { webSocketService, TransactionProcessedData, AnalysisCompletedData, CaseCreatedData } from '../services/websocket'

export interface RealtimeTransaction {
  id: string
  invoiceId: string
  vendorName: string
  amount: number
  timestamp: string
  status: 'processed' | 'analyzing' | 'flagged' | 'completed'
  riskScore?: number
  riskLevel?: 'low' | 'medium' | 'high'
  caseId?: string
}

export interface RealtimeStats {
  totalProcessed: number
  totalFlagged: number
  avgProcessingTime: number
  highRiskCount: number
  lastUpdated: string
}

const useRealtimeMonitoring = () => {
  const [transactions, setTransactions] = useState<RealtimeTransaction[]>([])
  const [stats, setStats] = useState<RealtimeStats>({
    totalProcessed: 0,
    totalFlagged: 0,
    avgProcessingTime: 0,
    highRiskCount: 0,
    lastUpdated: new Date().toISOString()
  })
  const [isConnected, setIsConnected] = useState(false)

  // Initialize WebSocket connection
  useEffect(() => {
    webSocketService.connect()
    
    const checkConnection = () => {
      setIsConnected(webSocketService.isConnected())
    }
    
    // Check connection status periodically
    const interval = setInterval(checkConnection, 5000)
    
    return () => {
      clearInterval(interval)
      webSocketService.disconnect()
    }
  }, [])

  // Handle transaction processed events
  const handleTransactionProcessed = useCallback((data: TransactionProcessedData) => {
    const newTransaction: RealtimeTransaction = {
      id: data.transactionId,
      invoiceId: data.invoiceId,
      vendorName: data.vendorName,
      amount: data.amount,
      timestamp: data.timestamp,
      status: 'processed'
    }

    setTransactions(prev => [newTransaction, ...prev.slice(0, 9)]) // Keep last 10
    setStats(prev => ({
      ...prev,
      totalProcessed: prev.totalProcessed + 1,
      lastUpdated: new Date().toISOString()
    }))
  }, [])

  // Handle analysis completed events
  const handleAnalysisCompleted = useCallback((data: AnalysisCompletedData) => {
    setTransactions(prev => prev.map(tx => 
      tx.id === data.transactionId 
        ? { 
            ...tx, 
            status: data.riskLevel === 'high' ? 'flagged' : 'completed',
            riskScore: data.riskScore,
            riskLevel: data.riskLevel
          }
        : tx
    ))

    setStats(prev => ({
      ...prev,
      avgProcessingTime: (prev.avgProcessingTime * prev.totalProcessed + data.processingTimeMs) / (prev.totalProcessed + 1),
      highRiskCount: data.riskLevel === 'high' ? prev.highRiskCount + 1 : prev.highRiskCount,
      lastUpdated: new Date().toISOString()
    }))
  }, [])

  // Handle case created events
  const handleCaseCreated = useCallback((data: CaseCreatedData) => {
    setTransactions(prev => prev.map(tx => 
      tx.id === data.transactionId 
        ? { ...tx, caseId: data.caseId, status: 'flagged' }
        : tx
    ))

    setStats(prev => ({
      ...prev,
      totalFlagged: prev.totalFlagged + 1,
      lastUpdated: new Date().toISOString()
    }))
  }, [])

  // Subscribe to WebSocket events
  useEffect(() => {
    webSocketService.subscribe('transaction_processed', handleTransactionProcessed)
    webSocketService.subscribe('analysis_completed', handleAnalysisCompleted)
    webSocketService.subscribe('case_created', handleCaseCreated)

    return () => {
      webSocketService.unsubscribe('transaction_processed', handleTransactionProcessed)
      webSocketService.unsubscribe('analysis_completed', handleAnalysisCompleted)
      webSocketService.unsubscribe('case_created', handleCaseCreated)
    }
  }, [handleTransactionProcessed, handleAnalysisCompleted, handleCaseCreated])

  // Mock data for development/demo
  const generateMockTransaction = useCallback(() => {
    const vendors = ['Global Logistics Corp.', 'Tech Supplies Inc.', 'Office Solutions Ltd.', 'Construction Materials Co.', 'IT Services Group']
    const amounts = [5000, 7500, 12000, 9999.99, 15000, 2500, 18000]
    
    const mockTransaction: RealtimeTransaction = {
      id: `tx-${Date.now()}`,
      invoiceId: `INV-2024-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
      vendorName: vendors[Math.floor(Math.random() * vendors.length)],
      amount: amounts[Math.floor(Math.random() * amounts.length)],
      timestamp: new Date().toISOString(),
      status: 'processed'
    }

    handleTransactionProcessed({
      transactionId: mockTransaction.id,
      invoiceId: mockTransaction.invoiceId,
      vendorName: mockTransaction.vendorName,
      amount: mockTransaction.amount,
      timestamp: mockTransaction.timestamp
    })

    // Simulate analysis after 2-5 seconds
    setTimeout(() => {
      const riskScore = Math.floor(Math.random() * 100)
      const riskLevel = riskScore > 70 ? 'high' : riskScore > 40 ? 'medium' : 'low'
      
      handleAnalysisCompleted({
        transactionId: mockTransaction.id,
        riskScore,
        riskLevel,
        processingTimeMs: 1500 + Math.random() * 2000,
        timestamp: new Date().toISOString()
      })

      // Simulate case creation for high risk
      if (riskLevel === 'high') {
        setTimeout(() => {
          handleCaseCreated({
            caseId: `FLG-${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
            transactionId: mockTransaction.id,
            flagType: riskScore > 80 ? 'duplicate_invoice' : 'threshold_avoidance',
            riskScore,
            timestamp: new Date().toISOString()
          })
        }, 1000)
      }
    }, 2000 + Math.random() * 3000)
  }, [handleTransactionProcessed, handleAnalysisCompleted, handleCaseCreated])

  // Auto-generate mock transactions for demo
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance per interval
        generateMockTransaction()
      }
    }, 5000) // Every 5 seconds

    return () => clearInterval(interval)
  }, [generateMockTransaction])

  return {
    transactions,
    stats,
    isConnected,
    generateMockTransaction
  }
}

export default useRealtimeMonitoring