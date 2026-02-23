/**
 * Slide-in drawer panel from the right.
 */
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

export const Drawer = DialogPrimitive.Root;
export const DrawerTrigger = DialogPrimitive.Trigger;

export function DrawerContent({
  children,
  className,
  title,
}: {
  children: ReactNode;
  className?: string;
  title: string;
}) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-40 bg-black/40 overlay-blur animate-fade-in" />
      <DialogPrimitive.Content
        className={cn(
          'fixed right-0 top-0 bottom-0 z-50 w-full max-w-md',
          'border-l border-border bg-bg-card shadow-2xl',
          'animate-slide-in-right focus:outline-none',
          'flex flex-col',
          className,
        )}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <DialogPrimitive.Title className="text-base font-semibold text-text-primary">
            {title}
          </DialogPrimitive.Title>
          <DialogPrimitive.Close className="rounded-md p-1.5 text-text-muted hover:text-text-primary hover:bg-bg-card-hover transition-colors">
            <X size={16} />
          </DialogPrimitive.Close>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-4">{children}</div>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}



