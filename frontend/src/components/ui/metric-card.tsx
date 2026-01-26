import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  variant?: 'default' | 'profit' | 'cost' | 'neutral';
  badge?: string;
  badgeVariant?: 'success' | 'warning' | 'danger';
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function MetricCard({
  title,
  value,
  subtitle,
  variant = 'default',
  badge,
  badgeVariant = 'success',
  className,
  size = 'md',
}: MetricCardProps) {
  const sizeStyles = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const valueSizes = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl lg:text-5xl',
  };

  const variantStyles = {
    default: 'bg-card border border-border',
    profit: 'profit-gradient text-profit-foreground',
    cost: 'cost-gradient text-destructive-foreground',
    neutral: 'bg-secondary',
  };

  const badgeStyles = {
    success: 'bg-profit/20 text-profit-foreground',
    warning: 'bg-warning/20 text-warning-foreground',
    danger: 'bg-destructive/20 text-destructive-foreground',
  };

  return (
    <div
      className={cn(
        'rounded-xl card-shadow-lg transition-all duration-200 hover:scale-[1.02]',
        sizeStyles[size],
        variantStyles[variant],
        className
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <p
          className={cn(
            'text-sm font-medium uppercase tracking-wider',
            variant === 'default' ? 'text-muted-foreground' : 'opacity-80'
          )}
        >
          {title}
        </p>
        {badge && (
          <span
            className={cn(
              'px-2.5 py-1 rounded-full text-xs font-semibold',
              variant === 'profit' || variant === 'cost' 
                ? 'bg-white/20' 
                : badgeStyles[badgeVariant]
            )}
          >
            {badge}
          </span>
        )}
      </div>
      <p
        className={cn(
          'font-bold mt-2 animate-number',
          valueSizes[size],
          variant === 'default' && 'text-foreground'
        )}
      >
        {value}
      </p>
      {subtitle && (
        <p
          className={cn(
            'text-sm mt-1',
            variant === 'default' ? 'text-muted-foreground' : 'opacity-70'
          )}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
}
