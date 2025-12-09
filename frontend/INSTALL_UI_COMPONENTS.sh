#!/bin/bash

# Script to install all required shadcn/ui components for Admin Dashboard
# Run this from the frontend directory

echo "Installing shadcn/ui components for Admin Dashboard..."

# Install all required components
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add table

echo "All UI components installed successfully!"
echo ""
echo "Note: Some components may already exist and will be skipped."
