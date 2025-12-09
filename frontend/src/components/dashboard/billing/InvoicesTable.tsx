'use client'

import { format } from 'date-fns'
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
import { Download, Eye } from 'lucide-react'

export interface Invoice {
  id: string
  date: Date
  amount: number
  status: 'paid' | 'pending' | 'failed'
  description: string
  invoiceUrl?: string
  pdfUrl?: string
}

interface InvoicesTableProps {
  invoices: Invoice[]
}

export function InvoicesTable({ invoices }: InvoicesTableProps) {
  const handleDownload = (invoice: Invoice) => {
    if (invoice.pdfUrl) {
      window.open(invoice.pdfUrl, '_blank')
    }
  }

  const handleView = (invoice: Invoice) => {
    if (invoice.invoiceUrl) {
      window.open(invoice.invoiceUrl, '_blank')
    }
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {invoices.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                No invoices found
              </TableCell>
            </TableRow>
          ) : (
            invoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell className="font-medium">
                  {format(invoice.date, 'MMM dd, yyyy')}
                </TableCell>
                <TableCell>{invoice.description}</TableCell>
                <TableCell className="font-mono">
                  ${(invoice.amount / 100).toFixed(2)}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      invoice.status === 'paid'
                        ? 'default'
                        : invoice.status === 'pending'
                        ? 'secondary'
                        : 'destructive'
                    }
                  >
                    {invoice.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    {invoice.invoiceUrl && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleView(invoice)}
                        title="View Invoice"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}
                    {invoice.pdfUrl && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDownload(invoice)}
                        title="Download PDF"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
