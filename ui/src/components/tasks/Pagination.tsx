import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface PaginationProps {
  page: number;
  totalPages: number;
  totalCount: number;
  pageSize: number;
  onPageChange: (p: number) => void;
}

export function Pagination({
  page,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
}: PaginationProps) {
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, totalCount);

  return (
    <div className="flex items-center justify-between">
      <p className="text-xs text-text-muted">
        Showing {from}–{to} of {totalCount}
      </p>
      <div className="flex items-center gap-1">
        <Button
          variant="secondary"
          size="icon"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="px-3 text-xs text-text-secondary">
          {page} / {totalPages}
        </span>
        <Button
          variant="secondary"
          size="icon"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

