import { ReactNode } from 'react'
import { ArrowUp, ArrowDown, Minus } from 'lucide-react'
import { KPI } from '../../types'

interface KPIStatCardProps extends KPI {
  className?: string
}

const KPIStatCard = ({ 
  title, 
  value, 
  change, 
  description, 
  icon, 
  color,
  className = '' 
}: KPIStatCardProps) => {
  const colorClasses = {
    primary: 'bg-primary-50 border-primary-200 text-primary-700',
    success: 'bg-success-50 border-success-200 text-success-700',
    warning: 'bg-warning-50 border-warning-200 text-warning-700',
    danger: 'bg-danger-50 border-danger-200 text-danger-700',
    gray: 'bg-gray-50 border-gray-200 text-gray-700',
  }

  const iconComponents: Record<string, ReactNode> = {
    'trending-up': <ArrowUp className="h-4 w-4" />,
    'trending-down': <ArrowDown className="h-4 w-4" />,
    'minus': <Minus className="h-4 w-4" />,
  }

  return (
    <div className={`glass-card rounded-xl p-5 border ${colorClasses[color]} ${className} hover-lift`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <div className="flex items-baseline space-x-2">
            <p className="text-2xl font-semibold">{value}</p>
            {change !== undefined && (
              <div className={`flex items-center text-sm font-medium px-1.5 py-0.5 rounded ${
                change > 0 
                  ? 'bg-green-100 text-green-700' 
                  : change < 0 
                    ? 'bg-red-100 text-red-700' 
                    : 'bg-gray-100 text-gray-700'
              }`}>
                {iconComponents[change > 0 ? 'trending-up' : change < 0 ? 'trending-down' : 'minus']}
                <span className="ml-1">{Math.abs(change)}%</span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-2">{description}</p>
        </div>
        <div className={`p-2 rounded-lg ${colorClasses[color].replace('bg-', 'bg-').replace('text-', 'text-')}`}>
          {iconComponents[icon] || <div className="h-5 w-5" />}
        </div>
      </div>
    </div>
  )
}

export default KPIStatCard