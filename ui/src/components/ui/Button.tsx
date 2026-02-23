import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
  {
    variants: {
      variant: {
        primary: 'bg-accent text-white hover:bg-accent-hover',
        secondary:
          'bg-bg-card text-text-secondary border border-border hover:bg-bg-card-hover hover:text-text-primary',
        danger:
          'bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20',
        success:
          'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 hover:bg-emerald-500/20',
        warning:
          'bg-yellow-500/10 text-yellow-400 border border-yellow-500/25 hover:bg-yellow-500/20',
        ghost: 'text-text-secondary hover:bg-bg-card hover:text-text-primary',
      },
      size: {
        sm: 'h-7 px-2.5 text-xs rounded',
        md: 'h-9 px-4 text-sm',
        lg: 'h-10 px-5 text-sm',
        icon: 'h-8 w-8 p-0',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  },
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  ),
);

Button.displayName = 'Button';



