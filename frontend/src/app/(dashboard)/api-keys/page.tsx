'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, AlertCircle } from 'lucide-react'
import { ApiKeyTable, type ApiKey } from '@/components/dashboard/ApiKeyTable'
import { CreateApiKeyDialog } from '@/components/dashboard/CreateApiKeyDialog'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

// Mock data - TODO: Replace with actual API calls
const mockApiKeys: ApiKey[] = [
  {
    id: '1',
    name: 'Production Key',
    key: 'alo_prod_abc123def456ghi789jkl',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30),
    lastUsed: new Date(Date.now() - 1000 * 60 * 5),
    status: 'active',
  },
  {
    id: '2',
    name: 'Development Key',
    key: 'alo_dev_xyz789uvw456rst123mno',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15),
    lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 2),
    status: 'active',
  },
  {
    id: '3',
    name: 'Testing Key',
    key: 'alo_test_qwe098asd765zxc432bnm',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7),
    lastUsed: null,
    status: 'inactive',
  },
]

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  useEffect(() => {
    // TODO: Fetch from API
    setTimeout(() => {
      setApiKeys(mockApiKeys)
      setLoading(false)
    }, 500)
  }, [])

  const handleDelete = (id: string) => {
    // TODO: Call API to delete
    setApiKeys((prev) => prev.filter((key) => key.id !== id))
  }

  const handleRotate = (id: string) => {
    // TODO: Call API to rotate
    setApiKeys((prev) =>
      prev.map((key) =>
        key.id === id
          ? {
              ...key,
              key: `alo_${Math.random().toString(36).substring(2, 15)}`,
              createdAt: new Date(),
            }
          : key
      )
    )
  }

  const handleCreateSuccess = () => {
    // TODO: Refresh API keys from server
    // For now, we'll just close the dialog
    // The actual key refresh would happen in the CreateApiKeyDialog onSuccess
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-40" />
        </div>
        <Skeleton className="h-48" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">API Keys</h1>
          <p className="text-muted-foreground">
            Manage your API keys for accessing the AI Orchestra Gateway
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create New Key
        </Button>
      </div>

      {/* Security Notice */}
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Keep your API keys secure</AlertTitle>
        <AlertDescription>
          Never share your API keys publicly or commit them to version control.
          If a key is compromised, revoke it immediately and create a new one.
        </AlertDescription>
      </Alert>

      {/* Getting Started Card */}
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            Use these API keys to authenticate your requests to the AI Orchestra Gateway
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Include your API key in the Authorization header:
          </p>
          <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
            <code>
              {`curl -X POST https://api.ai-orchestra.com/v1/generate \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Hello, world!", "model": "claude-opus-4-5"}'`}
            </code>
          </pre>
        </CardContent>
      </Card>

      {/* API Keys Table */}
      <Card>
        <CardHeader>
          <CardTitle>Your API Keys</CardTitle>
          <CardDescription>
            {apiKeys.length} {apiKeys.length === 1 ? 'key' : 'keys'} total
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ApiKeyTable
            apiKeys={apiKeys}
            onDelete={handleDelete}
            onRotate={handleRotate}
          />
        </CardContent>
      </Card>

      {/* Create API Key Dialog */}
      <CreateApiKeyDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={handleCreateSuccess}
      />
    </div>
  )
}
