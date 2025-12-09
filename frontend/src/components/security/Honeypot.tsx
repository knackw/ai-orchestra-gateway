'use client'

import { forwardRef } from 'react'

/**
 * SEC-004: Honeypot Component
 *
 * A hidden form field that catches bots. Human users won't see or fill this field,
 * but automated bots typically fill all form fields they find.
 *
 * The field is:
 * - Visually hidden with CSS
 * - Removed from tab order
 * - Has misleading but tempting field names for bots
 * - Has autocomplete disabled
 *
 * @example
 * ```tsx
 * const honeypotRef = useRef<HTMLInputElement>(null)
 *
 * const onSubmit = (data) => {
 *   if (honeypotRef.current?.value) {
 *     // Bot detected - silently reject
 *     return
 *   }
 *   // Process legitimate submission
 * }
 *
 * <form>
 *   <Honeypot ref={honeypotRef} />
 *   ...other fields
 * </form>
 * ```
 */
interface HoneypotProps {
  /** Field name - use tempting names like 'website', 'url', 'company_url' */
  name?: string
}

export const Honeypot = forwardRef<HTMLInputElement, HoneypotProps>(
  function Honeypot({ name = 'website' }, ref) {
    return (
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          left: '-9999px',
          width: '1px',
          height: '1px',
          overflow: 'hidden',
        }}
      >
        <label htmlFor={`hp_${name}`} style={{ display: 'none' }}>
          Leave this field empty
        </label>
        <input
          ref={ref}
          type="text"
          id={`hp_${name}`}
          name={name}
          tabIndex={-1}
          autoComplete="off"
          aria-hidden="true"
          style={{
            position: 'absolute',
            left: '-9999px',
          }}
        />
      </div>
    )
  }
)
