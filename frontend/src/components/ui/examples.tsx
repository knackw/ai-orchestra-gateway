/**
 * UI Component Examples
 * Demonstrates usage of all UI components in the library
 *
 * This file serves as:
 * - Living documentation
 * - Component showcase
 * - Integration examples
 * - Testing reference
 */

"use client"

import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import {
  AlertCircle,
  Check,
  ChevronRight,
  Mail,
  Settings,
  User,
  Moon,
  Sun,
  Info,
  CheckCircle2,
  XCircle,
  AlertTriangle
} from "lucide-react"

// Import all UI components
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { Switch } from "@/components/ui/switch"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { ToastAction } from "@/components/ui/toast"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

/**
 * Example 1: Complete Form with Validation
 */
const formSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  role: z.string().min(1, "Please select a role"),
  terms: z.boolean().refine((val) => val === true, {
    message: "You must accept the terms and conditions",
  }),
  bio: z.string().max(500, "Bio must be less than 500 characters").optional(),
})

export function FormExample() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      role: "",
      terms: false,
      bio: "",
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    // TODO: Implement form submission
    void values // SEC-016: Prevent unused variable warning
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Create Account</CardTitle>
        <CardDescription>
          Fill in the form below to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="user@example.com" {...field} />
                  </FormControl>
                  <FormDescription>
                    We'll never share your email with anyone else.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="••••••••" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="role"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Role</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a role" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="user">User</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="developer">Developer</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="bio"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Bio</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Tell us about yourself"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Optional. Max 500 characters.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="terms"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>
                      Accept terms and conditions
                    </FormLabel>
                    <FormDescription>
                      You agree to our Terms of Service and Privacy Policy.
                    </FormDescription>
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full">
              Create Account
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}

/**
 * Example 2: Data Table with Actions
 */
const invoices = [
  { id: "INV001", status: "Paid", amount: "$250.00", date: "2024-01-15" },
  { id: "INV002", status: "Pending", amount: "$150.00", date: "2024-01-16" },
  { id: "INV003", status: "Unpaid", amount: "$350.00", date: "2024-01-17" },
  { id: "INV004", status: "Paid", amount: "$450.00", date: "2024-01-18" },
]

export function DataTableExample() {
  const { toast } = useToast()

  const handleAction = (invoiceId: string, action: string) => {
    toast({
      title: `Action: ${action}`,
      description: `Invoice ${invoiceId} - ${action} triggered`,
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Invoices</CardTitle>
        <CardDescription>
          A list of your recent invoices and their status
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableCaption>Your invoice history for the last 7 days</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Invoice</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Date</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {invoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell className="font-medium">{invoice.id}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      invoice.status === "Paid"
                        ? "success"
                        : invoice.status === "Pending"
                        ? "warning"
                        : "destructive"
                    }
                  >
                    {invoice.status}
                  </Badge>
                </TableCell>
                <TableCell>{invoice.date}</TableCell>
                <TableCell className="text-right">{invoice.amount}</TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        Actions
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleAction(invoice.id, "View")}
                      >
                        View details
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleAction(invoice.id, "Download")}
                      >
                        Download PDF
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleAction(invoice.id, "Delete")}
                        className="text-destructive"
                      >
                        Delete invoice
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

/**
 * Example 3: User Profile Card with Dialog
 */
export function UserProfileExample() {
  const [open, setOpen] = React.useState(false)

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="flex flex-row items-center gap-4">
        <Avatar className="h-16 w-16">
          <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
          <AvatarFallback>JD</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <CardTitle>John Doe</CardTitle>
          <CardDescription>john.doe@example.com</CardDescription>
        </div>
        <Badge variant="success">Active</Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <Label>Role</Label>
          <span className="text-sm text-muted-foreground">Administrator</span>
        </div>
        <Separator />
        <div className="flex items-center justify-between">
          <Label>Member since</Label>
          <span className="text-sm text-muted-foreground">January 2024</span>
        </div>
        <Separator />
        <div className="space-y-2">
          <Label>Account progress</Label>
          <Progress value={75} />
          <p className="text-xs text-muted-foreground">
            75% profile completion
          </p>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" className="flex-1">
              Edit Profile
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Profile</DialogTitle>
              <DialogDescription>
                Make changes to your profile here. Click save when you're done.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" defaultValue="John Doe" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" defaultValue="john.doe@example.com" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setOpen(false)}>Save changes</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        <Button className="flex-1">View Details</Button>
      </CardFooter>
    </Card>
  )
}

/**
 * Example 4: Alert Variations
 */
export function AlertExamples() {
  return (
    <div className="space-y-4 w-full max-w-2xl">
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Information</AlertTitle>
        <AlertDescription>
          This is an informational alert with default styling.
        </AlertDescription>
      </Alert>

      <Alert variant="success">
        <CheckCircle2 className="h-4 w-4" />
        <AlertTitle>Success</AlertTitle>
        <AlertDescription>
          Your changes have been saved successfully.
        </AlertDescription>
      </Alert>

      <Alert variant="warning">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Warning</AlertTitle>
        <AlertDescription>
          Please review the changes before proceeding.
        </AlertDescription>
      </Alert>

      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          An error occurred. Please try again later.
        </AlertDescription>
      </Alert>
    </div>
  )
}

/**
 * Example 5: Navigation with Tabs and Sheet
 */
export function NavigationExample() {
  return (
    <Card className="w-full max-w-3xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Settings</CardTitle>
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon">
                <Settings className="h-4 w-4" />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Advanced Settings</SheetTitle>
                <SheetDescription>
                  Configure advanced options for your application
                </SheetDescription>
              </SheetHeader>
              <div className="space-y-4 py-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="notifications">Notifications</Label>
                  <Switch id="notifications" />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <Label htmlFor="dark-mode">Dark Mode</Label>
                  <Switch id="dark-mode" />
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="account">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="account">Account</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
          </TabsList>
          <TabsContent value="account" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" placeholder="Enter username" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="Enter email" />
            </div>
          </TabsContent>
          <TabsContent value="security" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current-password">Current Password</Label>
              <Input id="current-password" type="password" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input id="new-password" type="password" />
            </div>
          </TabsContent>
          <TabsContent value="notifications" className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive email about your account activity
                </p>
              </div>
              <Switch />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Push Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive push notifications on your devices
                </p>
              </div>
              <Switch />
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

/**
 * Example 6: Loading States with Skeleton
 */
export function LoadingExample() {
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 3000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>User Profile</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Skeleton className="h-12 w-12 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </div>
            <Skeleton className="h-32 w-full" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" />
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold">John Doe</h3>
                <p className="text-sm text-muted-foreground">
                  john.doe@example.com
                </p>
              </div>
            </div>
            <p className="text-sm">
              Full-stack developer with 5 years of experience in building web
              applications. Passionate about clean code and user experience.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Example 7: Toast Notifications
 */
export function ToastExample() {
  const { toast } = useToast()

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Toast Notifications</CardTitle>
        <CardDescription>
          Click the buttons to see different toast notifications
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button
          onClick={() => {
            toast({
              title: "Success!",
              description: "Your action completed successfully.",
            })
          }}
          className="w-full"
        >
          Show Success Toast
        </Button>

        <Button
          variant="destructive"
          onClick={() => {
            toast({
              variant: "destructive",
              title: "Uh oh! Something went wrong.",
              description: "There was a problem with your request.",
            })
          }}
          className="w-full"
        >
          Show Error Toast
        </Button>

        <Button
          variant="outline"
          onClick={() => {
            toast({
              title: "Action Required",
              description: "Please confirm your email address.",
              action: <ToastAction altText="Verify">Verify</ToastAction>,
            })
          }}
          className="w-full"
        >
          Show Toast with Action
        </Button>
      </CardContent>
    </Card>
  )
}

/**
 * Main Showcase Component
 * Displays all examples in a grid
 */
export default function UIComponentShowcase() {
  return (
    <TooltipProvider>
      <div className="container mx-auto py-10 space-y-10">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold">UI Component Library</h1>
          <p className="text-muted-foreground">
            Production-ready components built with Radix UI and Tailwind CSS
          </p>
        </div>

        <Separator />

        <div className="grid gap-10">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Forms</h2>
            <FormExample />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Data Tables</h2>
            <DataTableExample />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">User Profiles</h2>
            <UserProfileExample />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Alerts</h2>
            <AlertExamples />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Navigation</h2>
            <NavigationExample />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Loading States</h2>
            <LoadingExample />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Notifications</h2>
            <ToastExample />
          </section>
        </div>
      </div>
    </TooltipProvider>
  )
}
