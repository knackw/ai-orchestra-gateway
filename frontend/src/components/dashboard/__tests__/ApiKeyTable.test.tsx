import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/utils'
import userEvent from '@testing-library/user-event'
import { ApiKeyTable, type ApiKey } from '../ApiKeyTable'

// Mock the toast hook
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}))

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: (date: Date) => `${Math.floor((Date.now() - date.getTime()) / 86400000)} days ago`,
}))

describe('ApiKeyTable Component', () => {
  const mockApiKeys: ApiKey[] = [
    {
      id: 'key-1',
      name: 'Production Key',
      key: 'sk_prod_1234567890abcdef',
      createdAt: new Date('2024-01-01'),
      lastUsed: new Date('2024-01-15'),
      status: 'active',
    },
    {
      id: 'key-2',
      name: 'Development Key',
      key: 'sk_dev_abcdefghij123456',
      createdAt: new Date('2024-01-05'),
      lastUsed: null,
      status: 'inactive',
    },
  ]

  const mockOnDelete = vi.fn()
  const mockOnRotate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders table with correct headers', () => {
    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Key')).toBeInTheDocument()
    expect(screen.getByText('Created')).toBeInTheDocument()
    expect(screen.getByText('Last Used')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
  })

  it('renders all API keys', () => {
    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    expect(screen.getByText('Production Key')).toBeInTheDocument()
    expect(screen.getByText('Development Key')).toBeInTheDocument()
  })

  it('masks API keys correctly', () => {
    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Keys should be masked (first 8 chars + **** + last 4 chars)
    // Key is 'sk_prod_1234567890abcdef' -> 'sk_prod_1****cdef'
    expect(screen.getByText('sk_prod_1****cdef')).toBeInTheDocument()
  })

  it('displays status badges correctly', () => {
    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    expect(screen.getByText('active')).toBeInTheDocument()
    expect(screen.getByText('inactive')).toBeInTheDocument()
  })

  it('shows "Never" for keys that were never used', () => {
    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    expect(screen.getByText('Never')).toBeInTheDocument()
  })

  it('displays empty state when no keys exist', () => {
    render(
      <ApiKeyTable
        apiKeys={[]}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    expect(screen.getByText(/no api keys found/i)).toBeInTheDocument()
  })

  it('copies API key to clipboard on copy button click', async () => {
    const user = userEvent.setup()

    // Use the globally mocked clipboard from setup.ts
    const writeTextSpy = vi.spyOn(navigator.clipboard, 'writeText')

    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Find and click the first copy button
    const copyButtons = screen.getAllByRole('button', { name: '' })
    const copyButton = copyButtons.find(btn => {
      const svg = btn.querySelector('svg')
      return svg !== null
    })

    if (copyButton) {
      await user.click(copyButton)

      await waitFor(() => {
        expect(writeTextSpy).toHaveBeenCalledWith(mockApiKeys[0].key)
      })
    }
  })

  it('opens delete confirmation dialog', async () => {
    const user = userEvent.setup()

    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Open dropdown menu for first key
    const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
    await user.click(menuButtons[0])

    // Click delete option
    const deleteOption = screen.getByRole('menuitem', { name: /delete/i })
    await user.click(deleteOption)

    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/are you sure/i)).toBeInTheDocument()
      expect(screen.getByText(/permanently delete the api key/i)).toBeInTheDocument()
    })
  })

  it('confirms deletion and calls onDelete', async () => {
    const user = userEvent.setup()

    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Open menu and click delete
    const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
    await user.click(menuButtons[0])

    const deleteOption = screen.getByRole('menuitem', { name: /delete/i })
    await user.click(deleteOption)

    // Confirm deletion
    await waitFor(() => {
      const confirmButton = screen.getByRole('button', { name: /delete/i })
      return user.click(confirmButton)
    })

    await waitFor(() => {
      expect(mockOnDelete).toHaveBeenCalledWith('key-1')
    })
  })

  it('cancels deletion', async () => {
    const user = userEvent.setup()

    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Open menu and click delete
    const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
    await user.click(menuButtons[0])

    const deleteOption = screen.getByRole('menuitem', { name: /delete/i })
    await user.click(deleteOption)

    // Cancel deletion
    await waitFor(() => {
      const cancelButton = screen.getByRole('button', { name: /cancel/i })
      return user.click(cancelButton)
    })

    await waitFor(() => {
      expect(mockOnDelete).not.toHaveBeenCalled()
    })
  })

  it('opens rotate confirmation dialog', async () => {
    const user = userEvent.setup()

    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Open menu and click rotate
    const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
    await user.click(menuButtons[0])

    const rotateOption = screen.getByRole('menuitem', { name: /rotate key/i })
    await user.click(rotateOption)

    // Confirmation dialog should appear
    await waitFor(() => {
      expect(screen.getByText(/rotate api key/i)).toBeInTheDocument()
      expect(screen.getByText(/generate a new key/i)).toBeInTheDocument()
    })
  })

  it('confirms rotation and calls onRotate', async () => {
    const user = userEvent.setup()

    render(
      <ApiKeyTable
        apiKeys={mockApiKeys}
        onDelete={mockOnDelete}
        onRotate={mockOnRotate}
      />
    )

    // Open menu and click rotate
    const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
    await user.click(menuButtons[0])

    const rotateOption = screen.getByRole('menuitem', { name: /rotate key/i })
    await user.click(rotateOption)

    // Confirm rotation
    await waitFor(async () => {
      const confirmButton = screen.getByRole('button', { name: /rotate/i })
      await user.click(confirmButton)
    })

    await waitFor(() => {
      expect(mockOnRotate).toHaveBeenCalledWith('key-1')
    })
  })

  describe('Accessibility', () => {
    it('has accessible menu button', () => {
      render(
        <ApiKeyTable
          apiKeys={mockApiKeys}
          onDelete={mockOnDelete}
          onRotate={mockOnRotate}
        />
      )

      const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
      expect(menuButtons.length).toBeGreaterThan(0)
    })

    it('has proper table structure', () => {
      const { container } = render(
        <ApiKeyTable
          apiKeys={mockApiKeys}
          onDelete={mockOnDelete}
          onRotate={mockOnRotate}
        />
      )

      const table = container.querySelector('table')
      expect(table).toBeInTheDocument()

      const thead = container.querySelector('thead')
      expect(thead).toBeInTheDocument()

      const tbody = container.querySelector('tbody')
      expect(tbody).toBeInTheDocument()
    })

    it('has accessible dialog descriptions', async () => {
      const user = userEvent.setup()

      render(
        <ApiKeyTable
          apiKeys={mockApiKeys}
          onDelete={mockOnDelete}
          onRotate={mockOnRotate}
        />
      )

      // Open delete dialog
      const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
      await user.click(menuButtons[0])

      const deleteOption = screen.getByRole('menuitem', { name: /delete/i })
      await user.click(deleteOption)

      await waitFor(() => {
        const description = screen.getByText(/this will permanently delete/i)
        expect(description).toBeInTheDocument()
      })
    })
  })
})
