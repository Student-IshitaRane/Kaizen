import { clsx } from 'clsx'

interface RiskBadgeProps {
  level: 'low' | 'medium' | 'high'
  score?: number
  showScore?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const RiskBadge = ({ level, score, showScore = false, size = 'md' }: RiskBadgeProps) => {
  const config = {
    low: {
      label: 'Low',
      color: 'bg-green-100 text-green-800 border border-green-200',
      dotColor: 'bg-green-500',
      textColor: 'text-green-800'
    },
    medium: {
      label: 'Medium',
      color: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
      dotColor: 'bg-yellow-500',
      textColor: 'text-yellow-800'
    },
    high: {
      label: 'High',
      color: 'bg-red-100 text-red-800 border border-red-200',
      dotColor: 'bg-red-500',
      textColor: 'text-red-800'
    }
  }[level]

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-sm'
  }

  return (
    <div className={clsx(
      'inline-flex items-center rounded-full font-medium',
      config.color,
      sizeClasses[size],
      'space-x-1.5'
    )}>
      <div className="flex items-center space-x-1.5">
        <div className={clsx('w-2 h-2 rounded-full', config.dotColor)}></div>
        <span className={clsx('font-medium', config.textColor)}>
          {config.label}
          {showScore && score !== undefined && ` (${score})`}
        </span>
      </div>
    </div>
  )
}

export default RiskBadge