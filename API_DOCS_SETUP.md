# API Documentation Setup

This document describes the OpenAPI-based API documentation setup for MecaPy.

## Overview

The MecaPy API documentation is built using **Mintlify** with automatic integration of the **OpenAPI specification** generated from the FastAPI application.

## Architecture

```
repos/docs/
├── openapi.json              # Generated OpenAPI 3.1 specification
├── openapi.yaml              # YAML version of OpenAPI spec
├── mint.json                 # Mintlify configuration with OpenAPI integration
├── Taskfile.yml              # Automation tasks including OpenAPI generation
├── api-reference/
│   ├── introduction.mdx      # API overview
│   ├── authentication.mdx    # OAuth2/PKCE authentication guide
│   ├── functions/            # Function endpoints
│   │   ├── deploy-from-git.mdx
│   │   ├── deploy.mdx
│   │   ├── list.mdx
│   │   ├── get.mdx
│   │   ├── execute.mdx
│   │   └── delete.mdx
│   ├── packages/             # Package endpoints
│   │   └── deploy-from-git.mdx
│   ├── jobs/                 # Job endpoints
│   │   ├── list.mdx
│   │   ├── get.mdx
│   │   └── result.mdx
│   └── auth/                 # Authentication endpoints
│       └── login.mdx
└── repos/api/
    └── generate_openapi.py   # Script to generate OpenAPI spec
```

## Features

### 1. Dynamic OpenAPI Integration

The documentation automatically pulls the OpenAPI specification from the live API:

**Production**: `https://api.mecapy.com/openapi.json`
**Local Dev**: `http://localhost:8000/openapi.json`

This means:
- ✅ Always synchronized with deployed API
- ✅ No manual regeneration needed
- ✅ Updates automatically with each API deployment

**For offline development** (optional):
```bash
# Generate static OpenAPI spec for offline work
task openapi
```

### 2. Mintlify Integration

The `mint.json` configuration includes:

```json
{
  "openapi": ["openapi.json"],
  "api": {
    "baseUrl": "https://api.mecapy.com",
    "auth": {
      "method": "bearer"
    },
    "playground": {
      "mode": "show"
    }
  }
}
```

Features:
- **Interactive API Playground**: Test API endpoints directly from docs
- **Bearer Token Authentication**: Secure API calls with JWT tokens
- **Automatic Schema Validation**: Request/response validation from OpenAPI spec

### 3. Endpoint Documentation

Each API endpoint has dedicated documentation with:

- **Request Parameters**: Path, query, and body parameters
- **Response Schemas**: Success and error response structures
- **Code Examples**: cURL, Python, JavaScript
- **Security Information**: Authentication requirements
- **Error Handling**: Common error codes and messages

### 4. Authentication Guide

Comprehensive authentication documentation covering:

- OAuth2 with PKCE flow
- Bearer token usage
- Keycloak configuration
- Security best practices
- Token refresh and validation

## Development Workflow

### 1. Update API Code

Make changes to the FastAPI routes in `repos/api/mecapy_api/routes/`:

```python
@router.post("/functions/deploy")
async def deploy_function(request: FunctionCreateRequest):
    """Deploy a new serverless function."""
    # Implementation
```

### 2. Regenerate OpenAPI Spec

```bash
cd repos/docs
task openapi
```

### 3. Preview Documentation

```bash
task preview
# Visit http://localhost:3000
```

### 4. Update Endpoint Documentation (Optional)

Manually enhance the auto-generated endpoint pages in `api-reference/`:

```mdx
---
title: "Deploy Function"
api: "POST /functions/deploy"
description: "Deploy a serverless function"
---

## Custom Section

Add custom examples, diagrams, or explanations here.
```

## OpenAPI Generation Script

The `generate_openapi.py` script:

1. **Mocks Environment Variables**: Sets required env vars for FastAPI initialization
2. **Imports Application**: Loads the FastAPI app instance
3. **Generates OpenAPI**: Calls `app.openapi()` to get the specification
4. **Adds Metadata**: Includes server URLs and security schemes
5. **Exports Files**: Saves JSON and YAML versions

Example output:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "MecaPy API",
    "version": "0.1.2",
    "description": "API for MecaPy with Keycloak authentication"
  },
  "servers": [
    {
      "url": "https://api.mecapy.com",
      "description": "Production server"
    }
  ],
  "components": {
    "securitySchemes": {
      "OAuth2": { ... },
      "BearerAuth": { ... }
    }
  }
}
```

## Available Tasks

```bash
# View all available tasks
task --list

# Install Mintlify CLI
task install

# Start development server
task preview

# Regenerate OpenAPI spec
task openapi

# Build for production
task build

# Check for broken links
task check

# Clean build artifacts
task clean
```

## Deployment

The documentation can be deployed to:

1. **Mintlify Cloud**: Connect GitHub repo for automatic deployment
2. **Vercel/Netlify**: Deploy the built static files
3. **Custom Hosting**: Use the `.mintlify` output directory

### Mintlify Cloud Deployment

1. Connect GitHub repository at https://dashboard.mintlify.com
2. Configure via `mint.json`
3. Push changes trigger automatic deployment
4. Custom domain configuration available

## Best Practices

### 1. Keep OpenAPI Spec Updated

Regenerate the OpenAPI spec after any API changes:

```bash
task openapi
```

### 2. Enhance Auto-Generated Docs

While Mintlify auto-generates pages from OpenAPI, add custom content:

- Usage examples
- Architecture diagrams
- Common workflows
- Troubleshooting guides

### 3. Version API Documentation

For API versioning, create separate OpenAPI specs:

```
openapi-v1.json
openapi-v2.json
```

Update `mint.json`:

```json
{
  "openapi": ["openapi-v1.json", "openapi-v2.json"]
}
```

### 4. Test API Playground

Ensure the interactive playground works:

1. Start docs server: `task preview`
2. Navigate to any endpoint page
3. Test the "Try it" feature
4. Verify authentication works

## Troubleshooting

### OpenAPI Generation Fails

**Issue**: Environment variables missing

**Solution**: The script mocks required variables. If new variables are added to `config.py`, update `generate_openapi.py`:

```python
os.environ.setdefault("NEW_VARIABLE", "mock-value")
```

### Mintlify Server Errors

**Issue**: MDX parsing errors

**Solution**: Check for:
- Unescaped special characters (`<`, `>`, `€`)
- Invalid frontmatter YAML syntax
- Missing closing tags in code blocks

### Endpoint Pages Not Loading

**Issue**: "Could not find a page to redirect to"

**Solution**: Ensure all pages in `mint.json` navigation exist:

```bash
# Check for missing files
grep -r "api-reference/" mint.json | while read line; do
  file=$(echo $line | sed 's/.*"\(api-reference[^"]*\)".*/\1.mdx/')
  [ ! -f "$file" ] && echo "Missing: $file"
done
```

## Resources

- [Mintlify Documentation](https://mintlify.com/docs)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [FastAPI OpenAPI](https://fastapi.tiangolo.com/advanced/extending-openapi/)
- [Mintlify API Playground](https://mintlify.com/docs/api-playground/openapi-setup)

## Next Steps

1. **Add More Examples**: Enhance endpoint documentation with real-world examples
2. **Add Guides**: Create tutorial guides for common workflows
3. **Add SDKs**: Document Python SDK usage alongside REST API
4. **Add Webhooks**: Document webhook endpoints (if implemented)
5. **Add Rate Limiting**: Document API rate limits and quotas
