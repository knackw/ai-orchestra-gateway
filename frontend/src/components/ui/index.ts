/**
 * AI Legal Ops Gateway - UI Component Library
 * Central export file for all shadcn-style UI components
 *
 * All components are production-ready with:
 * - TypeScript with proper types
 * - forwardRef for DOM access
 * - className prop for extensibility
 * - Dark mode support
 * - Full accessibility (ARIA)
 */

// Layout & Structure
export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from "./card"
export { Separator } from "./separator"

// Navigation & Interaction
export { Button, buttonVariants, type ButtonProps } from "./button"
export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription
} from "./dialog"
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
} from "./dropdown-menu"
export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
} from "./sheet"
export { Tabs, TabsList, TabsTrigger, TabsContent } from "./tabs"
export { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "./accordion"
export {
  AlertDialog,
  AlertDialogPortal,
  AlertDialogOverlay,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
} from "./alert-dialog"
export { Popover, PopoverTrigger, PopoverContent } from "./popover"
export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "./tooltip"

// Forms & Inputs
export { Input, type InputProps } from "./input"
export { Textarea, type TextareaProps } from "./textarea"
export { Label } from "./label"
export { Checkbox } from "./checkbox"
export { Switch } from "./switch"
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from "./select"
export { RadioGroup, RadioGroupItem } from "./radio-group"
export { Slider } from "./slider"
export {
  useFormField,
  Form,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  FormField,
} from "./form"

// Data Display
export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
} from "./table"
export { DataTable } from "./data-table"
export { Badge, badgeVariants, type BadgeProps } from "./badge"
export { Avatar, AvatarImage, AvatarFallback } from "./avatar"

// Feedback
export { Alert, AlertTitle, AlertDescription } from "./alert"
export {
  type ToastProps,
  type ToastActionElement,
  ToastProvider,
  ToastViewport,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction,
} from "./toast"
export { Toaster } from "./toaster"
export { Progress } from "./progress"
export { Skeleton } from "./skeleton"
