# UI Component Library - AI Legal Ops Gateway

**Version:** 2.0
**Style:** shadcn/ui inspired
**Framework:** Next.js 15 + React 19 + TypeScript

## Overview

Vollständige, produktionsreife UI Component Library mit:

- **TypeScript** - Vollständige Typsicherheit
- **Tailwind CSS** - Utility-first Styling
- **Radix UI** - Headless UI Primitives für Accessibility
- **Class Variance Authority (CVA)** - Type-safe Variants
- **Dark Mode** - Vollständige Theme-Unterstützung
- **Accessibility** - WCAG 2.1 AA konform

## Component Catalog

### Layout & Structure

#### Card
**Location:** `src/components/ui/card.tsx`

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here.</p>
  </CardContent>
  <CardFooter>
    <p>Card footer</p>
  </CardFooter>
</Card>
```

**Features:**
- Flexible composition
- Shadow & border styling
- Responsive padding

#### Separator
**Location:** `src/components/ui/separator.tsx`

```tsx
import { Separator } from "@/components/ui/separator"

<Separator orientation="horizontal" />
<Separator orientation="vertical" />
```

---

### Navigation & Interaction

#### Button
**Location:** `src/components/ui/button.tsx`

```tsx
import { Button } from "@/components/ui/button"

// Variants
<Button variant="default">Default</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="default">Default</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon">
  <Icon />
</Button>
```

**Props:**
- `variant`: default | destructive | outline | secondary | ghost | link
- `size`: default | sm | lg | icon
- `asChild`: Render as child component (Radix Slot)

#### Dialog
**Location:** `src/components/ui/dialog.tsx`

```tsx
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        Dialog description text
      </DialogDescription>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      <Button>Save</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Features:**
- Modal overlay
- Focus trap
- Escape key to close
- Accessible (ARIA)

#### Dropdown Menu
**Location:** `src/components/ui/dropdown-menu.tsx`

```tsx
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open Menu</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Logout</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

#### Sheet (Slide-over)
**Location:** `src/components/ui/sheet.tsx`

```tsx
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"

<Sheet>
  <SheetTrigger asChild>
    <Button>Open Sheet</Button>
  </SheetTrigger>
  <SheetContent side="right">
    <SheetHeader>
      <SheetTitle>Sheet Title</SheetTitle>
      <SheetDescription>
        Sheet description
      </SheetDescription>
    </SheetHeader>
    {/* Content */}
  </SheetContent>
</Sheet>
```

**Props:**
- `side`: right | left | top | bottom

#### Tabs
**Location:** `src/components/ui/tabs.tsx`

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    Account settings content
  </TabsContent>
  <TabsContent value="password">
    Password settings content
  </TabsContent>
</Tabs>
```

#### Tooltip
**Location:** `src/components/ui/tooltip.tsx`

```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>Hover me</TooltipTrigger>
    <TooltipContent>
      <p>Tooltip content</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

---

### Forms & Inputs

#### Form (react-hook-form Integration)
**Location:** `src/components/ui/form.tsx`

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const formSchema = z.object({
  username: z.string().min(2, "Username must be at least 2 characters"),
})

function MyForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="Enter username" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

#### Input
**Location:** `src/components/ui/input.tsx`

```tsx
import { Input } from "@/components/ui/input"

<Input type="text" placeholder="Enter text" />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" />
<Input type="number" placeholder="Number" />
<Input disabled placeholder="Disabled" />
```

#### Textarea
**Location:** `src/components/ui/textarea.tsx`

```tsx
import { Textarea } from "@/components/ui/textarea"

<Textarea placeholder="Enter your message" rows={4} />
```

#### Label
**Location:** `src/components/ui/label.tsx`

```tsx
import { Label } from "@/components/ui/label"

<Label htmlFor="email">Email</Label>
<Input id="email" type="email" />
```

#### Checkbox
**Location:** `src/components/ui/checkbox.tsx`

```tsx
import { Checkbox } from "@/components/ui/checkbox"

<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <label htmlFor="terms">Accept terms and conditions</label>
</div>
```

#### Switch
**Location:** `src/components/ui/switch.tsx`

```tsx
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

<div className="flex items-center space-x-2">
  <Switch id="airplane-mode" />
  <Label htmlFor="airplane-mode">Airplane Mode</Label>
</div>
```

#### Select
**Location:** `src/components/ui/select.tsx`

```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
    <SelectItem value="option3">Option 3</SelectItem>
  </SelectContent>
</Select>
```

---

### Data Display

#### Table
**Location:** `src/components/ui/table.tsx`

```tsx
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

<Table>
  <TableCaption>A list of your recent invoices.</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead>Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>INV001</TableCell>
      <TableCell>Paid</TableCell>
      <TableCell>$250.00</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

#### Badge
**Location:** `src/components/ui/badge.tsx`

```tsx
import { Badge } from "@/components/ui/badge"

<Badge variant="default">Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
<Badge variant="success">Success</Badge>
<Badge variant="warning">Warning</Badge>
```

**Props:**
- `variant`: default | secondary | destructive | outline | success | warning

#### Avatar
**Location:** `src/components/ui/avatar.tsx`

```tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>
```

---

### Feedback

#### Alert
**Location:** `src/components/ui/alert.tsx`

```tsx
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

<Alert variant="default">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components to your app using the cli.
  </AlertDescription>
</Alert>

<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Your session has expired. Please log in again.
  </AlertDescription>
</Alert>

<Alert variant="success">
  <AlertTitle>Success!</AlertTitle>
  <AlertDescription>
    Your changes have been saved.
  </AlertDescription>
</Alert>
```

**Props:**
- `variant`: default | destructive | success | warning

#### Toast
**Location:** `src/components/ui/toast.tsx`, `src/hooks/use-toast.ts`

```tsx
import { useToast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"

function MyComponent() {
  const { toast } = useToast()

  return (
    <Button
      onClick={() => {
        toast({
          title: "Scheduled: Catch up",
          description: "Friday, February 10, 2023 at 5:57 PM",
        })
      }}
    >
      Show Toast
    </Button>
  )
}

// Destructive variant
toast({
  variant: "destructive",
  title: "Uh oh! Something went wrong.",
  description: "There was a problem with your request.",
})

// With action
toast({
  title: "Email sent",
  description: "Your message has been sent successfully.",
  action: <ToastAction altText="Undo">Undo</ToastAction>,
})
```

**Note:** Add `<Toaster />` to your app layout:

```tsx
import { Toaster } from "@/components/ui/toaster"

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  )
}
```

#### Progress
**Location:** `src/components/ui/progress.tsx`

```tsx
import { Progress } from "@/components/ui/progress"

<Progress value={60} className="w-full" />
```

#### Skeleton
**Location:** `src/components/ui/skeleton.tsx`

```tsx
import { Skeleton } from "@/components/ui/skeleton"

<div className="flex items-center space-x-4">
  <Skeleton className="h-12 w-12 rounded-full" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>
```

---

## Utility Functions

### cn (classNames utility)
**Location:** `src/lib/utils.ts`

```tsx
import { cn } from "@/lib/utils"

// Merge Tailwind classes with proper precedence
<div className={cn("bg-red-500", isActive && "bg-blue-500")} />
```

**Features:**
- Merges multiple className strings
- Handles conditional classes
- Resolves Tailwind class conflicts (last wins)

---

## Styling & Theming

### CSS Variables
**Location:** `src/app/globals.css`

All components use CSS variables for theming:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  /* ... */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```

### Dark Mode
**Using:** `next-themes`

```tsx
import { ThemeProvider } from "next-themes"

<ThemeProvider attribute="class" defaultTheme="system" enableSystem>
  {children}
</ThemeProvider>
```

Toggle theme:

```tsx
import { useTheme } from "next-themes"

const { theme, setTheme } = useTheme()

<Button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
  Toggle Theme
</Button>
```

---

## Accessibility

All components are built with accessibility in mind:

- **Keyboard Navigation:** Full keyboard support
- **Screen Readers:** Proper ARIA labels and roles
- **Focus Management:** Visible focus indicators
- **Color Contrast:** WCAG AA compliant
- **Semantic HTML:** Proper use of semantic elements

### ARIA Best Practices

```tsx
// Button
<Button aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>

// Dialog
<Dialog>
  <DialogContent aria-describedby="dialog-description">
    <DialogTitle>Title</DialogTitle>
    <DialogDescription id="dialog-description">
      Description
    </DialogDescription>
  </DialogContent>
</Dialog>
```

---

## Testing

All components are testable with React Testing Library:

```tsx
import { render, screen } from "@testing-library/react"
import { Button } from "@/components/ui/button"

test("renders button with text", () => {
  render(<Button>Click me</Button>)
  expect(screen.getByText("Click me")).toBeInTheDocument()
})
```

---

## Dependencies

```json
{
  "@radix-ui/react-*": "^1.x.x",
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "lucide-react": "^0.468.0",
  "react-hook-form": "^7.54.2",
  "@hookform/resolvers": "^3.9.1",
  "zod": "^3.24.1",
  "tailwind-merge": "^2.5.5",
  "tailwindcss-animate": "^1.0.7",
  "next-themes": "^0.4.4"
}
```

---

## Best Practices

### 1. Component Composition

```tsx
// Good: Composable components
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// Avoid: Prop-heavy components
<Card title="Title" content="Content" />
```

### 2. Type Safety

```tsx
// Good: Use proper types
import { ButtonProps } from "@/components/ui/button"

interface MyButtonProps extends ButtonProps {
  customProp: string
}

// Good: Type inference
const formSchema = z.object({
  email: z.string().email(),
})

type FormData = z.infer<typeof formSchema>
```

### 3. Accessibility

```tsx
// Good: Proper labeling
<Label htmlFor="email">Email</Label>
<Input id="email" type="email" />

// Good: ARIA labels
<Button aria-label="Close dialog">
  <X />
</Button>
```

### 4. Performance

```tsx
// Good: forwardRef for performance
const MyComponent = React.forwardRef<HTMLDivElement, Props>(
  (props, ref) => <div ref={ref} {...props} />
)
```

---

## Migration Guide

### From Custom Components to shadcn

```tsx
// Before: Custom Button
<button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Click me
</button>

// After: shadcn Button
<Button variant="default">Click me</Button>
```

---

## Support & Resources

- **Component Source:** `/frontend/src/components/ui/`
- **Hooks:** `/frontend/src/hooks/`
- **Utils:** `/frontend/src/lib/utils.ts`
- **Tailwind Config:** `/frontend/tailwind.config.ts`
- **Global Styles:** `/frontend/src/app/globals.css`

---

## License

MIT License - AI Legal Ops Gateway
