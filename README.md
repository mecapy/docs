# 📚 MecaPy Documentation

> Official documentation for the MecaPy scientific computing platform

## Overview

This directory contains the complete MecaPy documentation, powered by [Mintlify](https://mintlify.com).

## Quick Start

### Prerequisites

- Node.js 18+ installed
- npm or pnpm package manager
- [Task](https://taskfile.dev) (optional but recommended)

### Installation & Launch

```bash
# Install Mintlify globally
task install

# Start development server
task dev
```

The documentation will be available at `http://localhost:3000`

## Available Commands

### Development

```bash
# Start development server (default port 3000)
task dev

# Start on custom port
task dev:port PORT=3001

# Preview documentation
task preview
```

### Build & Validation

```bash
# Build for production
task build

# Validate mint.json configuration
task validate

# Check for broken links
task check
```

### Initialization

```bash
# Initialize documentation structure
task init

# Quick start (init + dev server)
task start
```

### Utilities

```bash
# Show Mintlify info and version
task info

# Clean build artifacts
task clean

# List all available tasks
task --list
```

## Manual Usage (without Task)

If you prefer not to use Task:

```bash
# Install Mintlify
npm install -g mintlify

# Start dev server
mintlify dev

# Build
mintlify build

# Check broken links
mintlify broken-links
```

## Documentation Structure

```
docs/
├── mint.json                    # Mintlify configuration
├── Taskfile.yml                 # Task automation
├── README.md                    # This file
│
├── QUICKSTART.md                # Quick start guide
├── architecture.md              # Architecture overview
│
├── packages/                    # Package development docs
│   ├── MANIFEST_FORMAT.md       # Manifest specification
│   ├── STANDARD_TYPES_GUIDE.md  # Type system guide
│   ├── PACKAGE_MULTI_FUNCTIONS.md
│   ├── VERSIONING_STRATEGY.md
│   └── VERSIONING_REFINED.md
│
├── architecture/                # Architecture documentation
│   ├── architecture_finale_sans_limite.md
│   ├── architecture_serverless_simple.md
│   ├── execution_securisee_analyse.md
│   └── firecracker_faisabilite.md
│
├── api-reference/              # API documentation
│   ├── api-specifications.md
│   ├── authentication-providers.md
│   └── database-schema.md
│
└── ci-cd/                      # CI/CD documentation
    ├── container_registry_strategy.md
    └── registry_cicd_workflow.md
```

## Configuration

The documentation is configured via `mint.json`:

```json
{
  "$schema": "https://mintlify.com/schema.json",
  "name": "MecaPy Documentation",
  "navigation": [
    {
      "group": "Get Started",
      "pages": ["QUICKSTART", "architecture"]
    },
    ...
  ]
}
```

### Customization

Edit `mint.json` to:
- Modify navigation structure
- Change color scheme
- Add/remove pages
- Configure topbar links
- Set up social links

## Writing Documentation

Mintlify supports:

- **Markdown**: Standard GitHub-flavored markdown
- **MDX**: React components in markdown
- **Code blocks**: Syntax highlighting for 100+ languages
- **Tabs**: Multi-language code examples
- **Accordions**: Collapsible content sections
- **API endpoints**: OpenAPI/Swagger integration

### Example: Code Block with Tabs

````markdown
<CodeGroup>

```python Python
def calculate(force: float) -> dict:
    return {"result": force * 2}
```

```javascript JavaScript
function calculate(force) {
  return { result: force * 2 };
}
```

</CodeGroup>
````

### Example: API Endpoint

Mintlify provides the `ResponseExample` component to display API responses with syntax highlighting. Wrap your JSON response in this component for a clean presentation in the documentation.

## Deployment

### Mintlify Cloud (Recommended)

1. Connect GitHub repository to Mintlify
2. Configure via `mint.json`
3. Push changes to trigger automatic deployment

### Self-Hosted

```bash
# Build static files
task build

# Deploy to hosting (Vercel, Netlify, etc.)
# Output in .mintlify directory
```

## Troubleshooting

### Port already in use

```bash
# Use custom port
task dev:port PORT=3001
```

### Invalid JSON configuration

```bash
# Validate mint.json
task validate
```

### Broken links

```bash
# Check for broken links
task check
```

### Clear cache

```bash
# Clean build artifacts
task clean
```

## Resources

- [Mintlify Documentation](https://mintlify.com/docs)
- [Mintlify Components](https://mintlify.com/docs/content/components)
- [Mintlify GitHub](https://github.com/mintlify/mint)
- [Task Documentation](https://taskfile.dev)

## Contributing

When adding new documentation:

1. Create/edit markdown files in appropriate directories
2. Update `mint.json` navigation
3. Test locally with `task dev`
4. Validate with `task validate`
5. Check for broken links with `task check`
6. Commit and push changes

## Support

For documentation issues:
- Create an issue in the main MecaPy repository
- Contact: support@mecapy.com

---

**Happy documenting!** 📝
