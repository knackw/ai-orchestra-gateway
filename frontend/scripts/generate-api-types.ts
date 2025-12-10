/**
 * SEC-013: OpenAPI TypeScript Client Generator
 *
 * Generates TypeScript types from the FastAPI backend's OpenAPI schema.
 * This ensures type safety between frontend and backend.
 *
 * Usage:
 *   npm run generate:api-types
 *
 * Requirements:
 *   - Backend must be running at BACKEND_URL (default: http://localhost:8000)
 *   - Backend must have openapi.json endpoint available
 */

import * as fs from 'fs'
import * as path from 'path'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
const OUTPUT_DIR = path.join(__dirname, '../src/types/generated')
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'api-types.ts')

interface OpenAPISchema {
  openapi: string
  info: {
    title: string
    version: string
  }
  paths: Record<string, PathItem>
  components?: {
    schemas?: Record<string, SchemaObject>
  }
}

interface PathItem {
  get?: Operation
  post?: Operation
  put?: Operation
  patch?: Operation
  delete?: Operation
}

interface Operation {
  operationId?: string
  summary?: string
  description?: string
  parameters?: Parameter[]
  requestBody?: RequestBody
  responses: Record<string, Response>
  tags?: string[]
}

interface Parameter {
  name: string
  in: 'path' | 'query' | 'header' | 'cookie'
  required?: boolean
  schema: SchemaObject
  description?: string
}

interface RequestBody {
  content?: {
    'application/json'?: {
      schema: SchemaObject
    }
  }
  required?: boolean
}

interface Response {
  description: string
  content?: {
    'application/json'?: {
      schema: SchemaObject
    }
  }
}

interface SchemaObject {
  type?: string
  format?: string
  $ref?: string
  items?: SchemaObject
  properties?: Record<string, SchemaObject>
  required?: string[]
  allOf?: SchemaObject[]
  anyOf?: SchemaObject[]
  oneOf?: SchemaObject[]
  enum?: (string | number)[]
  description?: string
  nullable?: boolean
  default?: unknown
}

/**
 * Convert OpenAPI type to TypeScript type
 */
function openApiTypeToTs(schema: SchemaObject, schemas: Record<string, SchemaObject>): string {
  if (schema.$ref) {
    const refName = schema.$ref.split('/').pop() || 'unknown'
    return refName
  }

  if (schema.allOf) {
    return schema.allOf.map(s => openApiTypeToTs(s, schemas)).join(' & ')
  }

  if (schema.anyOf || schema.oneOf) {
    const types = (schema.anyOf || schema.oneOf)!
    return types.map(s => openApiTypeToTs(s, schemas)).join(' | ')
  }

  if (schema.enum) {
    return schema.enum.map(v => typeof v === 'string' ? `'${v}'` : String(v)).join(' | ')
  }

  switch (schema.type) {
    case 'string':
      if (schema.format === 'date-time') return 'string' // ISO 8601 datetime
      if (schema.format === 'date') return 'string' // ISO 8601 date
      if (schema.format === 'uuid') return 'string'
      if (schema.format === 'email') return 'string'
      if (schema.format === 'uri') return 'string'
      return 'string'

    case 'integer':
    case 'number':
      return 'number'

    case 'boolean':
      return 'boolean'

    case 'array':
      if (schema.items) {
        return `Array<${openApiTypeToTs(schema.items, schemas)}>`
      }
      return 'unknown[]'

    case 'object':
      if (schema.properties) {
        const props = Object.entries(schema.properties).map(([key, prop]) => {
          const isRequired = schema.required?.includes(key)
          const tsType = openApiTypeToTs(prop, schemas)
          const nullable = prop.nullable ? ' | null' : ''
          return `  ${key}${isRequired ? '' : '?'}: ${tsType}${nullable}`
        })
        return `{\n${props.join('\n')}\n}`
      }
      return 'Record<string, unknown>'

    case 'null':
      return 'null'

    default:
      return 'unknown'
  }
}

/**
 * Generate TypeScript interface from OpenAPI schema
 */
function generateInterface(name: string, schema: SchemaObject, schemas: Record<string, SchemaObject>): string {
  const lines: string[] = []

  if (schema.description) {
    lines.push(`/**`)
    lines.push(` * ${schema.description}`)
    lines.push(` */`)
  }

  if (schema.enum) {
    const values = schema.enum.map(v => typeof v === 'string' ? `'${v}'` : String(v)).join(' | ')
    lines.push(`export type ${name} = ${values}`)
  } else if (schema.allOf) {
    const types = schema.allOf.map(s => openApiTypeToTs(s, schemas)).join(' & ')
    lines.push(`export type ${name} = ${types}`)
  } else if (schema.type === 'object' || schema.properties) {
    lines.push(`export interface ${name} {`)
    if (schema.properties) {
      for (const [propName, propSchema] of Object.entries(schema.properties)) {
        const isRequired = schema.required?.includes(propName)
        const tsType = openApiTypeToTs(propSchema, schemas)
        const nullable = propSchema.nullable ? ' | null' : ''

        if (propSchema.description) {
          lines.push(`  /** ${propSchema.description} */`)
        }
        lines.push(`  ${propName}${isRequired ? '' : '?'}: ${tsType}${nullable}`)
      }
    }
    lines.push(`}`)
  } else {
    lines.push(`export type ${name} = ${openApiTypeToTs(schema, schemas)}`)
  }

  return lines.join('\n')
}

/**
 * Generate RFC 7807 Problem Detail type
 */
function generateProblemDetailType(): string {
  return `
/**
 * RFC 7807 Problem Details for HTTP APIs
 *
 * Standardized error response format used by the backend.
 * See: https://datatracker.ietf.org/doc/html/rfc7807
 */
export interface ProblemDetail {
  /** URI reference identifying the problem type */
  type: string
  /** Short human-readable summary */
  title: string
  /** HTTP status code */
  status: number
  /** Human-readable explanation specific to this occurrence */
  detail?: string
  /** URI reference to the specific occurrence */
  instance?: string
  /** Correlation ID for distributed tracing */
  trace_id?: string
  /** ISO 8601 timestamp */
  timestamp?: string
}
`
}

/**
 * Main generation function
 */
async function generateTypes(): Promise<void> {
  console.log(`Fetching OpenAPI schema from ${BACKEND_URL}/openapi.json...`)

  try {
    const response = await fetch(`${BACKEND_URL}/openapi.json`)

    if (!response.ok) {
      throw new Error(`Failed to fetch OpenAPI schema: ${response.status} ${response.statusText}`)
    }

    const schema: OpenAPISchema = await response.json()
    console.log(`Found OpenAPI ${schema.openapi} - ${schema.info.title} v${schema.info.version}`)

    const schemas = schema.components?.schemas || {}
    const generatedTypes: string[] = []

    // Header
    generatedTypes.push(`/**
 * SEC-013: Auto-generated TypeScript types from OpenAPI schema
 *
 * DO NOT EDIT THIS FILE MANUALLY!
 * Generated from: ${BACKEND_URL}/openapi.json
 * Generated at: ${new Date().toISOString()}
 * API Version: ${schema.info.version}
 *
 * To regenerate:
 *   npm run generate:api-types
 */

/* eslint-disable */
// @ts-nocheck - Auto-generated file
`)

    // Add RFC 7807 Problem Detail type
    generatedTypes.push(generateProblemDetailType())

    // Generate types for all schemas
    for (const [name, schemaObj] of Object.entries(schemas)) {
      // Skip internal/validation error schemas that are not useful in frontend
      if (name.startsWith('HTTPValidationError') || name.startsWith('ValidationError')) {
        continue
      }

      generatedTypes.push('')
      generatedTypes.push(generateInterface(name, schemaObj, schemas))
    }

    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true })
    }

    // Write the generated file
    fs.writeFileSync(OUTPUT_FILE, generatedTypes.join('\n'))
    console.log(`Generated types written to: ${OUTPUT_FILE}`)

    // Count generated types
    const typeCount = Object.keys(schemas).length
    console.log(`Successfully generated ${typeCount} TypeScript types`)

  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error generating types: ${error.message}`)

      // Create a fallback file with core types
      console.log('Creating fallback types file with core types...')

      const fallbackTypes = `/**
 * SEC-013: Core API Types (Fallback)
 *
 * These are core types used when the OpenAPI schema is not available.
 * Run \`npm run generate:api-types\` with the backend running to get
 * the complete generated types.
 */

${generateProblemDetailType()}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data?: T
  error?: ProblemDetail
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  limit?: number
  offset?: number
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

/**
 * Date range filter
 */
export interface DateRangeFilter {
  start_date?: string
  end_date?: string
}

/**
 * Common timestamp fields
 */
export interface TimestampFields {
  created_at: string
  updated_at: string
}
`

      if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true })
      }
      fs.writeFileSync(OUTPUT_FILE, fallbackTypes)
      console.log(`Fallback types written to: ${OUTPUT_FILE}`)
    }

    process.exit(1)
  }
}

// Run the generator
generateTypes()
