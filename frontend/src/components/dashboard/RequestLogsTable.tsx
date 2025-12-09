'use client'

import { useState } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDistanceToNow } from 'date-fns'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export interface RequestLog {
  id: string
  timestamp: string
  endpoint: string
  method: string
  model: string
  tokens: number
  credits: number
  status: 'success' | 'error'
  responseTime: number
  statusCode: number
}

interface RequestLogsTableProps {
  logs: RequestLog[]
  totalCount?: number
  currentPage?: number
  pageSize?: number
  onPageChange?: (page: number) => void
}

export function RequestLogsTable({
  logs,
  totalCount = logs.length,
  currentPage = 1,
  pageSize = 10,
  onPageChange,
}: RequestLogsTableProps) {
  const totalPages = Math.ceil(totalCount / pageSize)
  const canGoPrevious = currentPage > 1
  const canGoNext = currentPage < totalPages

  const handlePrevious = () => {
    if (canGoPrevious && onPageChange) {
      onPageChange(currentPage - 1)
    }
  }

  const handleNext = () => {
    if (canGoNext && onPageChange) {
      onPageChange(currentPage + 1)
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>Endpoint</TableHead>
              <TableHead>Model</TableHead>
              <TableHead className="text-right">Tokens</TableHead>
              <TableHead className="text-right">Credits</TableHead>
              <TableHead className="text-right">Response Time</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground h-24">
                  No request logs found
                </TableCell>
              </TableRow>
            ) : (
              logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                    {formatDistanceToNow(new Date(log.timestamp), {
                      addSuffix: true,
                    })}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-mono text-sm">{log.endpoint}</span>
                      <span className="text-xs text-muted-foreground">
                        {log.method}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm">{log.model}</TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {log.tokens.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {log.credits.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right text-sm text-muted-foreground">
                    {log.responseTime.toFixed(2)}s
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={log.status === 'success' ? 'default' : 'destructive'}
                    >
                      {log.statusCode}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing{' '}
            <span className="font-medium">
              {(currentPage - 1) * pageSize + 1}
            </span>{' '}
            to{' '}
            <span className="font-medium">
              {Math.min(currentPage * pageSize, totalCount)}
            </span>{' '}
            of <span className="font-medium">{totalCount}</span> results
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevious}
              disabled={!canGoPrevious}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <div className="text-sm font-medium">
              Page {currentPage} of {totalPages}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNext}
              disabled={!canGoNext}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
