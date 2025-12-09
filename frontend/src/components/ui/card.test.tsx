import { describe, it, expect } from 'vitest'
import { render, screen } from '@/tests/utils'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from './card'

describe('Card Components', () => {
  describe('Card', () => {
    it('renders children correctly', () => {
      render(<Card>Card Content</Card>)
      expect(screen.getByText('Card Content')).toBeInTheDocument()
    })

    it('applies custom className', () => {
      render(<Card className="custom-card">Content</Card>)
      const card = screen.getByText('Content').closest('div')
      expect(card?.className).toContain('custom-card')
    })
  })

  describe('CardHeader', () => {
    it('renders correctly', () => {
      render(
        <Card>
          <CardHeader>Header Content</CardHeader>
        </Card>
      )
      expect(screen.getByText('Header Content')).toBeInTheDocument()
    })
  })

  describe('CardTitle', () => {
    it('renders as heading', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
          </CardHeader>
        </Card>
      )
      expect(screen.getByText('Test Title')).toBeInTheDocument()
    })
  })

  describe('CardDescription', () => {
    it('renders description text', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
        </Card>
      )
      expect(screen.getByText('Test Description')).toBeInTheDocument()
    })
  })

  describe('CardContent', () => {
    it('renders content area', () => {
      render(
        <Card>
          <CardContent>Main Content</CardContent>
        </Card>
      )
      expect(screen.getByText('Main Content')).toBeInTheDocument()
    })
  })

  describe('CardFooter', () => {
    it('renders footer area', () => {
      render(
        <Card>
          <CardFooter>Footer Content</CardFooter>
        </Card>
      )
      expect(screen.getByText('Footer Content')).toBeInTheDocument()
    })
  })

  describe('Full Card Structure', () => {
    it('renders complete card with all sections', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
            <CardDescription>Card description text</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Main card content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Action</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByText('Card Title')).toBeInTheDocument()
      expect(screen.getByText('Card description text')).toBeInTheDocument()
      expect(screen.getByText('Main card content goes here')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument()
    })
  })
})
