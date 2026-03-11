import { clsx } from 'clsx'

interface StatusBadgeProps {
  status: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const StatusBadge = ({ status, size = 'md', className = '' }: StatusBadgeProps) => {
  const statusConfig: Record<string, { color: string; label: string }> = {
    'new': { color: 'bg-blue-100 text-blue-800', label: 'New' },
    'in_review': { color: 'bg-yellow-100 text-yellow-800', label: 'In Review' },
    'assigned': { color: 'bg-purple-100 text-purple-800', label: 'Assigned' },
    'resolved': { color: 'bg-green-100 text-green-800', label: 'Resolved' },
    'dismissed': { color: 'bg-gray-100 text-gray-800', label: 'Dismissed' },
    'submitted': { color: 'bg-blue-100 text-blue-800', label: 'Submitted' },
    'approved': { color: 'bg-green-100 text-green-800', label: 'Approved' },
    'rejected': { color: 'bg-red-100 text-red-800', label: 'Rejected' },
    'flagged': { color: 'bg-orange-100 text-orange-800', label: 'Flagged' },
    'uploaded': { color: 'bg-blue-100 text-blue-800', label: 'Uploaded' },
    'validating': { color: 'bg-yellow-100 text-yellow-800', label: 'Validating' },
    'standardized': { color: 'bg-purple-100 text-purple-800', label: 'Standardized' },
    'stored': { color: 'bg-green-100 text-green-800', label: 'Stored' },
    'failed': { color: 'bg-red-100 text-red-800', label: 'Failed' },
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }

  const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', label: status }

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full font-medium',
        config.color,
        sizeClasses[size],
        className
      )}
    >
      {config.label}
    </span>
  )
}

export default StatusBadge