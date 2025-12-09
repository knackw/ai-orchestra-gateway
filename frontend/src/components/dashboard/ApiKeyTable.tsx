'use client'

import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Copy, MoreVertical, RotateCw, Trash2, Check } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export interface ApiKey {
  id: string
  name: string
  key: string // Masked key
  createdAt: Date
  lastUsed: Date | null
  status: 'active' | 'inactive'
}

interface ApiKeyTableProps {
  apiKeys: ApiKey[]
  onDelete: (id: string) => void
  onRotate: (id: string) => void
}

export function ApiKeyTable({ apiKeys, onDelete, onRotate }: ApiKeyTableProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [rotateDialogOpen, setRotateDialogOpen] = useState(false)
  const [selectedKey, setSelectedKey] = useState<ApiKey | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const { toast } = useToast()

  const handleCopy = async (key: string, id: string) => {
    await navigator.clipboard.writeText(key)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
    toast({
      title: 'Copied',
      description: 'API key copied to clipboard',
    })
  }

  const confirmDelete = (key: ApiKey) => {
    setSelectedKey(key)
    setDeleteDialogOpen(true)
  }

  const confirmRotate = (key: ApiKey) => {
    setSelectedKey(key)
    setRotateDialogOpen(true)
  }

  const handleDelete = () => {
    if (selectedKey) {
      onDelete(selectedKey.id)
      toast({
        title: 'Deleted',
        description: 'API key has been deleted',
      })
    }
    setDeleteDialogOpen(false)
    setSelectedKey(null)
  }

  const handleRotate = () => {
    if (selectedKey) {
      onRotate(selectedKey.id)
      toast({
        title: 'Rotated',
        description: 'API key has been rotated',
      })
    }
    setRotateDialogOpen(false)
    setSelectedKey(null)
  }

  const maskKey = (key: string) => {
    if (key.length <= 12) return key
    return `${key.substring(0, 8)}****${key.substring(key.length - 4)}`
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Key</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Last Used</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[70px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {apiKeys.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  No API keys found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              apiKeys.map((apiKey) => (
                <TableRow key={apiKey.id}>
                  <TableCell className="font-medium">{apiKey.name}</TableCell>
                  <TableCell className="font-mono text-sm">
                    <div className="flex items-center gap-2">
                      {maskKey(apiKey.key)}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={() => handleCopy(apiKey.key, apiKey.id)}
                      >
                        {copiedId === apiKey.id ? (
                          <Check className="h-3 w-3" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDistanceToNow(apiKey.createdAt, { addSuffix: true })}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {apiKey.lastUsed
                      ? formatDistanceToNow(apiKey.lastUsed, { addSuffix: true })
                      : 'Never'}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={apiKey.status === 'active' ? 'default' : 'secondary'}
                    >
                      {apiKey.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                          <span className="sr-only">Open menu</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => handleCopy(apiKey.key, apiKey.id)}
                        >
                          <Copy className="mr-2 h-4 w-4" />
                          Copy Key
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => confirmRotate(apiKey)}>
                          <RotateCw className="mr-2 h-4 w-4" />
                          Rotate Key
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => confirmDelete(apiKey)}
                          className="text-destructive"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the API key &quot;{selectedKey?.name}&quot;.
              This action cannot be undone and any applications using this key will
              stop working immediately.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Rotate Confirmation Dialog */}
      <AlertDialog open={rotateDialogOpen} onOpenChange={setRotateDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rotate API Key?</AlertDialogTitle>
            <AlertDialogDescription>
              This will generate a new key for &quot;{selectedKey?.name}&quot;. The old
              key will stop working immediately. Make sure to update your
              applications with the new key.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRotate}>Rotate</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
