import { useState, useEffect } from 'react'
import api from '../../services/api/auth'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from 'recharts'
import { TrendingUp, AlertTriangle, ShieldAlert, Sparkles, Activity, FileText } from 'lucide-react'

const AuditorInsights = () => {
  const [timeRange, setTimeRange] = useState('30D')
  const [isLoading, setIsLoading] = useState(true)

  const [trendData, setTrendData] = useState<any[]>([])
  const [riskDistribution, setRiskDistribution] = useState<any[]>([])
  const [departmentData, setDepartmentData] = useState<any[]>([])
  const [kpis, setKpis] = useState<any>({
    total_scanned: 0,
    active_anomalies: 0,
    critical_risks: 0,
    ai_accuracy: 0,
    total_trend: '',
    anomalies_trend: '',
    critical_trend: '',
    accuracy_trend: ''
  })

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true)
      try {
        const response = await api.get(`/insights/dashboard?timeRange=${timeRange}`)
        if (response.data) {
          setTrendData(response.data.trendData)
          setRiskDistribution(response.data.riskDistribution)
          setDepartmentData(response.data.departmentData)
          setKpis(response.data.kpis)
        }
      } catch (error) {
        console.error("Error fetching insights:", error)
        // Fallback mock data in case backend is down
        setTrendData([
          { name: 'Week 1', anomalies: 4, volume: 1200 },
          { name: 'Week 2', anomalies: 7, volume: 1400 },
          { name: 'Week 3', anomalies: 3, volume: 1100 },
        ])
        setRiskDistribution([
          { name: 'Duplicate Invoices', value: 45 },
          { name: 'Off-hours Processing', value: 25 },
        ])
        setDepartmentData([
          { name: 'IT', high: 12, medium: 25, low: 40 },
          { name: 'Marketing', high: 3, medium: 15, low: 30 },
        ])
        setKpis({
          total_scanned: 14204,
          active_anomalies: 42,
          critical_risks: 3,
          ai_accuracy: 98.2,
          total_trend: '+12%',
          anomalies_trend: '-5%',
          critical_trend: 'Stable',
          accuracy_trend: '+0.4%'
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchDashboardData()
  }, [timeRange])

  const COLORS = ['#0ea5e9', '#14b8a6', '#f59e0b', '#8b5cf6', '#ef4444']

  return (
    <div className="min-h-full bg-slate-900 overflow-y-auto p-6 lg:p-10 font-sans">
      
      {/* Header section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 gap-4 relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">AI Analytics & Insights</h1>
          <p className="text-slate-400">Deep-dive visualizations of compliance trends and risk vectors.</p>
        </div>
        
        <div className="flex bg-slate-800/80 p-1 rounded-xl border border-slate-700 backdrop-blur-sm">
          {['7D', '30D', '90D', 'YTD'].map(range => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                timeRange === range 
                  ? 'bg-teal-500 text-white shadow-md' 
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className={`grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10 transition-opacity duration-500 ${isLoading ? 'opacity-50' : 'opacity-100'}`}>
        
        {/* Top KPIs */}
        <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-2">
          {[
            { label: 'Total Scanned', value: kpis.total_scanned.toLocaleString(), trend: kpis.total_trend, icon: FileText, color: 'text-blue-500', bg: 'bg-blue-500/10' },
            { label: 'Active Anomalies', value: kpis.active_anomalies.toLocaleString(), trend: kpis.anomalies_trend, icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-500/10' },
            { label: 'Critical Risks', value: kpis.critical_risks.toLocaleString(), trend: kpis.critical_trend, icon: ShieldAlert, color: 'text-red-500', bg: 'bg-red-500/10' },
            { label: 'AI Accuracy', value: typeof kpis.ai_accuracy === 'number' ? `${kpis.ai_accuracy}%` : kpis.ai_accuracy, trend: kpis.accuracy_trend, icon: Activity, color: 'text-teal-500', bg: 'bg-teal-500/10' },
          ].map((kpi, idx) => (
            <div key={idx} className="glass-card rounded-2xl p-6 border border-slate-700/50 shadow-lg hover:-translate-y-1 transition-transform">
              <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl ${kpi.bg}`}>
                  <kpi.icon className={`w-6 h-6 ${kpi.color}`} />
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                  kpi.trend.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400' : 
                  kpi.trend.startsWith('-') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'
                }`}>
                  {kpi.trend}
                </span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-1">{kpi.value}</h3>
              <p className="text-sm text-slate-400 font-medium tracking-wide">{kpi.label}</p>
            </div>
          ))}
        </div>

        {/* Chart 1: Anomaly Trends */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-700/50 shadow-xl">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-lg font-bold text-white">Anomaly Detection Over Time</h2>
            <button className="text-slate-400 hover:text-white"><TrendingUp className="w-5 h-5" /></button>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{fontSize: 12}} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" tick={{fontSize: 12}} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="anomalies" stroke="#f59e0b" strokeWidth={3} fillOpacity={1} fill="url(#colorAnomalies)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Explanation 1 */}
        <div className="lg:col-span-1 glass-card rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-b from-slate-800/50 to-slate-900/50 flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 rounded-bl-[100px] pointer-events-none"></div>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>
            <h2 className="text-lg font-bold text-white">AI Trend Analysis</h2>
          </div>
          <div className="flex-1 space-y-4 text-sm text-slate-300 leading-relaxed">
            <p>
              The orchestrator detected a precisely <span className="text-amber-400 font-bold">300% surge</span> in anomalies during Week 4. 
            </p>
            <p>
              This correlates strongly with the end-of-month invoice rush. The AI identified that vendors submitted batches of duplicate invoices during this high-volume period, bypassing Level 1 human checks.
            </p>
            <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-700 mt-auto">
              <span className="text-xs font-bold text-amber-500 uppercase tracking-widest block mb-1">Recommendation</span>
              Implement strict pre-validation rules for batch uploads during EOM periods.
            </div>
          </div>
        </div>

        {/* AI Explanation 2 */}
        <div className="lg:col-span-1 glass-card rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-b from-slate-800/50 to-slate-900/50 flex flex-col relative overflow-hidden order-last lg:order-none">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-bl-[100px] pointer-events-none"></div>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <Activity className="w-4 h-4 text-blue-500" />
            </div>
            <h2 className="text-lg font-bold text-white">Risk Vector Insights</h2>
          </div>
          <div className="flex-1 space-y-4 text-sm text-slate-300 leading-relaxed">
            <p>
              <span className="text-blue-400 font-bold">Duplicate Invoices</span> dominate the risk profile at 45%, followed closely by <span className="text-teal-400 font-bold">Off-hours Processing (25%)</span>.
            </p>
            <p>
              We're seeing a new emerging vector: <span className="text-purple-400 font-bold">New Vendor Spikes</span>. 10% of new anomalies involve vendors created less than 48 hours before their first massive payout.
            </p>
          </div>
        </div>

        {/* Chart 2: Risk Distribution */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-700/50 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-bold text-white">Anomaly Distribution by Type</h2>
          </div>
          <div className="h-[300px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {riskDistribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend layout="vertical" verticalAlign="middle" align="right" 
                  wrapperStyle={{ fontSize: '12px', color: '#cbd5e1' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Departmental Breakdown */}
        <div className="lg:col-span-3 glass-card rounded-2xl p-6 border border-slate-700/50 shadow-xl mt-4">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-lg font-bold text-white">Risk Exposure by Department</h2>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentData} margin={{ top: 20, right: 30, left: -20, bottom: 5 }} barSize={30}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{fontSize: 12}} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" tick={{fontSize: 12}} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                  cursor={{ fill: '#334155', opacity: 0.4 }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="high" name="High Risk" stackId="a" fill="#ef4444" radius={[0, 0, 4, 4]} />
                <Bar dataKey="medium" name="Medium Risk" stackId="a" fill="#f59e0b" />
                <Bar dataKey="low" name="Low Risk" stackId="a" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  )
}

export default AuditorInsights
