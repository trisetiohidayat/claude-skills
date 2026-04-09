---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt

## Overview

This is a comprehensive suite of tools designed for creating elaborate, multi-component HTML artifacts for claude.ai conversations. The system leverages modern frontend technologies to build complex, interactive artifacts that can include state management, routing, and rich UI components.

## Quick Start

### Prerequisites

- Node.js 18+ (automatically detected and pinned)
- npm or yarn

### Installation & Setup

1. **Initialize the frontend repo** using the provided initialization script
2. **Develop your artifact** by editing the generated code
3. **Bundle all code** into a single HTML file using the bundling script
4. **Display artifact** to user
5. (Optional) **Test the artifact**

## Tech Stack

The Web Artifacts Builder uses:
- React 18 + TypeScript (via Vite)
- Tailwind CSS 3.4.1 with shadcn/ui theming system
- Path aliases (`@/`) configured
- 40+ shadcn/ui components pre-installed
- All Radix UI dependencies included
- Parcel configured for bundling

## Design Guidelines

To avoid "AI slop" aesthetic issues:
- Avoid excessive centered layouts
- Avoid purple gradients
- Avoid uniform rounded corners
- Avoid Inter font

## Usage

### Step 1: Initialize Project

```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

### Step 2: Develop Your Artifact

Edit the generated files in the project directory. Use the common development tasks as guidance.

### Step 3: Bundle to Single HTML File

```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. The file can be directly shared in Claude conversations as an artifact.

**Requirements**: The project must have an `index.html` in the root directory.

### Step 4: Share Artifact

Share the bundled HTML file in conversation with the user so they can view it as an artifact.

### Step 5: Testing (Optional)

To test/visualize the artifact, use available tools including Playwright or Puppeteer. Testing is optional and typically performed after presenting the artifact if issues arise.

## shadcn/ui Components

The project includes 40+ pre-installed shadcn/ui components. For component documentation, visit: https://ui.shadcn.com/docs/components

## License

Complete terms are available in LICENSE.txt
