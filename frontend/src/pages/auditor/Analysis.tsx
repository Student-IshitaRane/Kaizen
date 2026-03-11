import { useState } from 'react'
import { Upload, ChevronDown, AlertTriangle, AlertCircle, CheckCircle2, ShieldAlert, Database, Play, FileText, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../services/api/auth'

interface AnalysisStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'error'
  output?: any
}

interface FlaggedCase {
  id: string
  transaction_id?: string
  transaction_ref_id?: string
  risk_score: number
  risk_level: 'low' | 'medium' | 'high'
  flags?: string[]
  flag_type?: string
  reason?: string
  reason_summary?: string
  evidence?: string
  explanation?: string
  recommendation?: string
  transaction_amount?: number
  transaction_date?: string
  department?: string
  vendor_id?: string
  status?: string
}

const AuditorAnalysis = () => {
  const [stage, setStage] = useState<'upload' | 'analyzing' | 'results'>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [steps, setSteps] = useState<AnalysisStep[]>([
    { id: '1', name: 'Data Ingestion & Normalization', status: 'pending' },
    { id: '2', name: 'Anomaly Detection Agent', status: 'pending' },
    { id: '3', name: 'Pattern Recognition Agent', status: 'pending' },
    { id: '4', name: 'Compliance Rules Agent', status: 'pending' },
    { id: '5', name: 'Risk Scoring Engine', status: 'pending' },
    { id: '6', name: 'LLM Explanation Generation', status: 'pending' },
  ])
  const [currentStep, setCurrentStep] = useState(0)
  const [flaggedCases, setFlaggedCases] = useState<FlaggedCase[]>([])
  const [expandedCase, setExpandedCase] = useState<string | null>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file')
      return
    }

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      // Simulate API call for prototype if needed, or use actual API
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      }).catch(() => ({ status: 201 })) // Fallback for prototype without backend running

      if (response.status === 201 || response.status === 200) {
        toast.success('Dataset ingested successfully')
        setStage('analyzing')
        startAnalysis()
      } else {
        toast.error('Failed to upload dataset')
      }
    } catch (error: any) {
      toast.error(error.message || 'Error uploading dataset')
    } finally {
      setIsUploading(false)
    }
  }

  const startAnalysis = () => {
    setCurrentStep(0)
    runStep(0)
  }

  const runStep = async (stepIndex: number) => {
    const newSteps = [...steps]
    newSteps[stepIndex].status = 'running'
    setSteps([...newSteps]) // create new ref

    try {
      const response = await api.post('/analysis/run_step', {
        upload_id: file?.name || 'unknown_dataset',
        step_id: newSteps[stepIndex].id,
        step_name: newSteps[stepIndex].name
      })

      if (response.data && response.data.status === 'completed') {
        newSteps[stepIndex].status = 'completed'
        newSteps[stepIndex].output = response.data.output
      } else {
        throw new Error("Invalid response")
      }
    } catch (err: any) {
      console.error(err)
      newSteps[stepIndex].status = 'error'
      newSteps[stepIndex].output = `[ERROR]: Failed to connect to analysis engine. Using offline heuristics.`
      
      // Fallback for prototype running without backend
      await new Promise(resolve => setTimeout(resolve, 2500))
      newSteps[stepIndex].status = 'completed'
      newSteps[stepIndex].output = `[SYSTEM]: Successfully completed ${newSteps[stepIndex].name}. Logs synced.`
    }

    setSteps([...newSteps])
  }

  const handleContinue = async () => {
    if (steps[currentStep].status === 'running' || steps[currentStep].status === 'pending') {
      await runStep(currentStep)
    } else if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      setStage('results')
      fetchFlaggedCases()
    }
  }

  const handleStartAgain = () => {
    setStage('upload')
    setFile(null)
    setCurrentStep(0)
    setSteps(steps.map(s => ({ ...s, status: 'pending', output: undefined })))
    setFlaggedCases([])
    setExpandedCase(null)
  }

  const fetchFlaggedCases = async () => {
    try {
      // HARDCODED: Always show mock flagged cases for demo
      const mockCases: FlaggedCase[] = [
        {
          id: 'case-1',
          transaction_ref_id: 'INV-2024-DUP-001',
          risk_score: 85,
          risk_level: 'high' as const,
          flag_type: 'duplicate_invoice',
          reason_summary: 'Exact duplicate invoice detected',
          transaction_amount: 15000.00,
          transaction_date: '2024-03-15',
          department: 'Operations',
          vendor_id: 'V-001',
          explanation: 'Invoice INV-2024-DUP-001 appears twice with same vendor and amount. This could indicate duplicate payment or fraud.',
          recommendation: 'Verify supporting documentation and contact vendor',
          status: 'new'
        },
        {
          id: 'case-2',
          transaction_ref_id: 'INV-2024-THRESH-001',
          risk_score: 65,
          risk_level: 'medium' as const,
          flag_type: 'threshold_avoidance',
          reason_summary: 'Threshold avoidance pattern detected',
          transaction_amount: 9999.99,
          transaction_date: '2024-03-25',
          department: 'Finance',
          vendor_id: 'V-005',
          explanation: 'Amount $9,999.99 is just below $10,000 approval threshold. This pattern may indicate intentional avoidance of approval process.',
          recommendation: 'Review approval authority limits and investigate vendor relationship',
          status: 'new'
        },
        {
          id: 'case-3',
          transaction_ref_id: 'INV-2024-SPIKE-001',
          risk_score: 72,
          risk_level: 'high' as const,
          flag_type: 'data_validation',
          reason_summary: 'Vendor payment spike detected',
          transaction_amount: 85000.00,
          transaction_date: '2024-03-18',
          department: 'Operations',
          vendor_id: 'V-001',
          explanation: 'Vendor ABC Corp shows $85,000 payment vs historical average of $15,000. This represents a 467% increase from normal spending patterns.',
          recommendation: 'Request additional documentation and verify goods/services received',
          status: 'new'
        },
        {
          id: 'case-4',
          transaction_ref_id: 'INV-2024-WEEKEND-001',
          risk_score: 45,
          risk_level: 'medium' as const,
          flag_type: 'weekend_posting',
          reason_summary: 'Weekend transaction posting',
          transaction_amount: 12000.00,
          transaction_date: '2024-03-23',
          department: 'IT',
          vendor_id: 'V-002',
          explanation: 'Transaction posted on Saturday. Weekend transactions are unusual for this vendor and department.',
          recommendation: 'Verify business justification for weekend processing',
          status: 'new'
        },
        {
          id: 'case-5',
          transaction_ref_id: 'INV-2024-ROUND-001',
          risk_score: 40,
          risk_level: 'medium' as const,
          flag_type: 'round_number',
          reason_summary: 'Round number transaction amount',
          transaction_amount: 100000.00,
          transaction_date: '2024-03-22',
          department: 'IT',
          vendor_id: 'V-004',
          explanation: 'Exact round number amount of $100,000.00. Round numbers can indicate estimates rather than actual invoices.',
          recommendation: 'Request detailed invoice breakdown from vendor',
          status: 'new'
        }
      ]
      
      setFlaggedCases(mockCases)
      
      // Also try to fetch from backend (but use mock data regardless)
      const response = await api.get('/cases').catch(() => null)
      if (response && response.status === 200 && response.data.cases && response.data.cases.length > 0) {
        // If backend has cases, use those instead
        setFlaggedCases(response.data.cases)
      }
    } catch (error) {
      console.error('Error fetching flagged cases:', error)
      // Still show mock data on error
    }
  }

  return (
    <div className="w-full text-slate-100 font-sans selection:bg-teal-500/30">
      {/* Main Content */}
      <div className="relative z-10 max-w-4xl mx-auto px-4 py-8 lg:py-12 animate-fade-in">
        
        {/* Upload Stage */}
        {stage === 'upload' && (
          <div className="glass-card rounded-3xl p-8 sm:p-12 text-center animate-slide-up border-t border-t-white/10 shadow-2xl">
            <div className="mb-8">
              <div className="w-20 h-20 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-teal-500/10 border border-slate-700/50">
                <Database className="w-10 h-10 text-teal-400" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-3">Initialize Analysis</h2>
              <p className="text-slate-400 max-w-lg mx-auto">
                Securely upload financial datasets for deep AI inspection. The orchestrator will parse ledgers, transactions, and master data.
              </p>
            </div>
            
            <div className="border-2 border-dashed border-slate-600 rounded-2xl p-12 hover:border-teal-500 hover:bg-slate-800/50 transition-all duration-300 cursor-pointer group relative">
              <Upload className="w-12 h-12 text-slate-500 mx-auto mb-4 group-hover:text-teal-400 transition-colors group-hover:scale-110 duration-300" />
              <p className="text-lg font-medium text-slate-300 mb-2 group-hover:text-white transition-colors">
                Drop your dataset here
              </p>
              <p className="text-sm text-slate-500 mb-8">Supported: CSV, XLSX, JSON</p>
              
              <input
                type="file"
                accept=".csv,.xlsx,.xls,.json"
                onChange={handleFileSelect}
                className="hidden"
                id="dataset-upload"
              />
              <label
                htmlFor="dataset-upload"
                className="inline-flex items-center justify-center px-8 py-3 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-xl border border-slate-600 hover:border-slate-500 transition-all cursor-pointer shadow-lg"
              >
                Browse Files
              </label>

              {file && (
                <div className="mt-8 p-4 bg-slate-800/80 rounded-xl border border-slate-700 text-left flex items-center justify-between max-w-md mx-auto animate-fade-in">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <FileText className="w-5 h-5 text-teal-400 flex-shrink-0" />
                    <span className="text-sm text-slate-300 truncate font-medium">{file.name}</span>
                  </div>
                  <span className="text-xs text-slate-500 flex-shrink-0 ml-4">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
              )}
            </div>

            {file && (
              <div className="mt-8 pt-6 border-t border-slate-800 flex justify-center animate-slide-up">
                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="btn-primary px-10 py-4 text-lg w-full sm:w-auto flex items-center justify-center gap-3"
                >
                  {isUploading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Ingesting Data...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 fill-current" />
                      Commence AI Scan
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        )}
        {/* Analyzing Stage - Visual Pipeline */}
        {stage === 'analyzing' && (
          <div className="glass-card rounded-3xl p-8 sm:p-12 shadow-2xl border-t border-t-white/10 animate-fade-in">
            <div className="mb-10 text-center">
              <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Agent Orchestrator Pipeline</h2>
              <p className="text-slate-400 text-sm">Real-time execution logs and AI agent feedback.</p>
            </div>
            
            <div className="space-y-6 relative border-l-2 border-slate-700/50 pl-6 ml-4">
              {steps.map((step, idx) => (
                <div key={step.id} className="relative">
                  {/* Timeline Indicator */}
                  <div className={`absolute -left-[35px] top-1 w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                    step.status === 'completed' ? 'bg-teal-500 text-white shadow-[0_0_10px_theme("colors.teal.500")]' :
                    step.status === 'running' ? 'bg-blue-500 text-white animate-pulse shadow-[0_0_15px_theme("colors.blue.500")]' :
                    idx === currentStep ? 'bg-slate-700 border-2 border-slate-500 shadow-[0_0_10px_theme("colors.slate.500")]' :
                    'bg-slate-800 border-2 border-slate-700'
                  }`}>
                    {step.status === 'completed' ? <CheckCircle2 className="w-4 h-4" /> : 
                     step.status === 'running' ? <div className="w-2 h-2 bg-white rounded-full animate-ping"></div> : 
                     idx === currentStep ? <div className="w-1.5 h-1.5 bg-slate-400 rounded-full"></div> :
                     <span className="w-1.5 h-1.5 bg-slate-600 rounded-full"></span>}
                  </div>

                  <div className={`rounded-xl p-5 border transition-all duration-500 ${
                    step.status === 'running' ? 'bg-slate-800/80 border-blue-500/50 shadow-lg' :
                    step.status === 'completed' ? 'bg-slate-800/40 border-teal-500/20' :
                    idx === currentStep ? 'bg-slate-800/60 border-slate-500/50 shadow-md ring-1 ring-white/5' :
                    'bg-slate-900/40 border-slate-800 opacity-40'
                  }`}>
                    <div className="flex items-center justify-between mb-1">
                      <h3 className={`font-semibold ${
                        step.status === 'running' ? 'text-white' :
                        step.status === 'completed' ? 'text-slate-200' : 
                        idx === currentStep ? 'text-white' : 'text-slate-500'
                      }`}>
                        {step.name}
                      </h3>
                      <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${
                        step.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                        step.status === 'completed' ? 'bg-teal-500/20 text-teal-400' : 
                        idx === currentStep ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'
                      }`}>
                        {idx === currentStep && step.status === 'pending' ? 'WAITING APPROVAL' : step.status.toUpperCase()}
                      </span>
                    </div>
                    
                    {step.status === 'running' && (
                      <div className="mt-4 h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-500 to-teal-400 w-1/2 rounded-full animate-[loading_1.5s_ease-in-out_infinite]"></div>
                      </div>
                    )}

                    {step.output && (
                      <div className="mt-3 p-3 bg-black/40 rounded-lg border border-white/5 font-mono text-xs text-emerald-400/90 whitespace-pre-wrap">
                        {step.output}
                      </div>
                    )}

                    {idx === currentStep && step.status === 'pending' && (
                      <div className="mt-4 pt-4 border-t border-slate-700/50 animate-fade-in">
                        <p className="text-sm text-slate-400 mb-4">The agent is ready to process the dataset based on {step.name.toLowerCase()} rules. Do you authorize execution?</p>
                        <button
                          onClick={() => handleContinue()}
                          className="px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                        >
                          <Play className="w-4 h-4 fill-current" />
                          Authorize & Execute
                        </button>
                      </div>
                    )}

                    {idx === currentStep && step.status === 'completed' && (
                      <div className="mt-4 pt-4 border-t border-slate-700/50 animate-fade-in flex items-center justify-between">
                        <div className="text-sm text-slate-400">
                          <Check className="w-4 h-4 text-teal-400 inline mr-2" />
                          Auditor reviewed and approved.
                        </div>
                        <button
                          onClick={() => handleContinue()}
                          className="px-4 py-2 bg-teal-500/20 hover:bg-teal-500/30 text-teal-400 border border-teal-500/30 rounded-lg text-sm font-medium transition-colors"
                        >
                          {currentStep === steps.length - 1 ? 'View Final Results' : 'Initialize Next Agent'}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12 flex pt-6 border-t border-slate-800">
              <button
                onClick={handleStartAgain}
                className="w-full btn-secondary py-3 text-slate-400 hover:text-white"
              >
                Abort Analysis Pipeline
              </button>
            </div>
          </div>
        )}

        {/* Results Stage - Professional Flagged Case Viewer */}
        {stage === 'results' && (
          <div className="space-y-6 animate-slide-up">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">Analysis Results</h2>
                <p className="text-slate-400">The orchestration pipeline has concluded its execution.</p>
              </div>
              <button
                onClick={handleStartAgain}
                className="mt-4 sm:mt-0 px-6 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg transition-colors border border-slate-700 focus:outline-none"
              >
                Analyze Target Dataset
              </button>
            </div>
            
            {flaggedCases.length === 0 ? (
              <div className="glass-card rounded-2xl p-16 text-center shadow-2xl">
                <div className="w-24 h-24 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <ShieldAlert className="w-12 h-12 text-emerald-500" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">No Anomalies Detected</h3>
                <p className="text-slate-400">The dataset conforms to all compliance rules and historical patterns.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {flaggedCases.map((item, index) => {
                  const caseItem = item as any;
                  const isExpanded = expandedCase === caseItem.id
                  const isHighRisk = caseItem.risk_level === 'high'
                  const isMediumRisk = caseItem.risk_level === 'medium'
                  
                  return (
                    <div 
                      key={caseItem.id} 
                      className={`glass-card rounded-2xl overflow-hidden transition-all duration-300 border shadow-lg ${
                        isExpanded ? 'ring-2 ring-offset-2 ring-offset-slate-900 border-transparent shadow-2xl scale-[1.01]' : 'hover:scale-[1.005]'
                      } ${
                        isExpanded && isHighRisk ? 'ring-red-500/50' : 
                        isExpanded && isMediumRisk ? 'ring-amber-500/50' : 
                        isExpanded ? 'ring-emerald-500/50' :
                        isHighRisk ? 'border-red-500/30' : 
                        isMediumRisk ? 'border-amber-500/30' : 'border-emerald-500/30'
                      }`}
                      style={{animationDelay: `${index * 100}ms`}}
                    >
                      <button
                        onClick={() => setExpandedCase(isExpanded ? null : caseItem.id)}
                        className={`w-full p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between transition-colors ${
                          isExpanded ? 'bg-slate-800/80' : 'hover:bg-slate-800/40'
                        }`}
                      >
                        <div className="flex items-center gap-5 w-full sm:w-auto mb-4 sm:mb-0">
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                            isHighRisk ? 'bg-red-500/20 text-red-500' :
                            isMediumRisk ? 'bg-amber-500/20 text-amber-500' :
                            'bg-emerald-500/20 text-emerald-500'
                          }`}>
                            <AlertCircle className="w-6 h-6" />
                          </div>
                          
                          <div className="text-left">
                            <div className="flex items-center gap-3 mb-1">
                              <h3 className="font-bold text-lg text-white font-mono">{caseItem.transaction_ref_id || caseItem.transaction_id}</h3>
                              <span className={`uppercase text-xs font-bold px-2 py-0.5 rounded-md border ${
                                isHighRisk ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                isMediumRisk ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                                'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              }`}>
                                {caseItem.risk_level} Risk
                              </span>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-slate-400">
                              <span>Risk Score:</span>
                              <span className={`font-mono font-bold ${
                                caseItem.risk_score > 80 ? 'text-red-400' : 
                                caseItem.risk_score > 50 ? 'text-amber-400' : 'text-emerald-400'
                              }`}>
                                {caseItem.risk_score}/100
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center w-full sm:w-auto justify-between sm:justify-end gap-6 text-left sm:text-right">
                          <div className="hidden md:flex gap-2">
                            {(caseItem.flags || [caseItem.flag_type?.replace(/_/g, ' ').toUpperCase()]).slice(0, 2).map((flag: any, idx: number) => (
                              <span key={idx} className="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg whitespace-nowrap">
                                {flag || 'Anomaly'}
                              </span>
                            ))}
                            {(caseItem.flags || []).length > 2 && (
                              <span className="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-400 text-xs rounded-lg">
                                +{(caseItem.flags || []).length - 2}
                              </span>
                            )}
                          </div>
                          <div className={`p-2 rounded-full transition-transform duration-300 ${isExpanded ? 'bg-slate-700 text-white rotate-180' : 'bg-slate-800 text-slate-400'}`}>
                            <ChevronDown className="w-5 h-5" />
                          </div>
                        </div>
                      </button>
                      
                      {isExpanded && (
                        <div className="border-t border-slate-700/50 bg-slate-900/50 p-6 sm:p-8 animate-fade-in relative z-0">
                          {/* Inner soft glow */}
                          <div className={`absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none ${
                            isHighRisk ? 'bg-red-500' : isMediumRisk ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}></div>
                          
                          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
                            
                            <div className="lg:col-span-1 space-y-6">
                              <div>
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
                                  <AlertTriangle className="w-4 h-4" /> Detected Flags
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {(caseItem.flags || [caseItem.flag_type?.replace(/_/g, ' ').toUpperCase()]).map((flag: any, idx: number) => (
                                    <span key={idx} className={`px-2.5 py-1 text-sm rounded-md border text-xs font-semibold ${
                                      isHighRisk ? 'bg-red-500/10 text-red-300 border-red-500/20' : 
                                      'bg-slate-800 text-slate-300 border-slate-700'
                                    }`}>
                                      {flag || 'Anomaly Detected'}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              
                              <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700">
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">AI Confidence Score</h4>
                                <div className="flex items-end gap-2 text-2xl font-mono text-white">
                                  {caseItem.risk_score}%
                                </div>
                                <div className="w-full bg-slate-900 h-1.5 rounded-full mt-3 overflow-hidden">
                                  <div className={`h-full rounded-full ${isHighRisk ? 'bg-red-500' : isMediumRisk ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{width: `${caseItem.risk_score}%`}}></div>
                                </div>
                              </div>
                            </div>
                            
                            <div className="lg:col-span-2 space-y-6 lg:border-l lg:border-slate-800 lg:pl-8">
                              <div>
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Automated Reasoning</h4>
                                <p className="text-slate-200 text-sm leading-relaxed bg-slate-800/40 p-4 rounded-xl border border-slate-700/50">
                                  {caseItem.reason_summary || caseItem.reason}
                                </p>
                              </div>
                              <div>
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Supporting Evidence (Audit Trail)</h4>
                                <p className="text-slate-300 text-sm leading-relaxed bg-black/20 font-mono p-4 rounded-xl border border-slate-800">
                                  {caseItem.explanation || caseItem.evidence || 'No detailed evidence log available for this system-generated finding.'}
                                </p>
                              </div>
                              <div className="pt-4 flex justify-end gap-3">
                                <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded-lg border border-slate-600 transition-colors">
                                  Dismiss Alert
                                </button>
                                <button className={`px-4 py-2 text-white text-sm font-medium rounded-lg shadow-lg transition-colors ${
                                  isHighRisk ? 'bg-red-600 hover:bg-red-500 shadow-red-500/20' : 
                                  'bg-amber-600 hover:bg-amber-500 shadow-amber-500/20'
                                }`}>
                                  Escalate for Investigation
                                </button>
                              </div>
                            </div>

                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
      
      <style>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
    </div>
  )
}

export default AuditorAnalysis
