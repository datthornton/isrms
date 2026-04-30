# ISRMS Development Guide

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/datthornton/isrms.git
cd isrms

# Install pnpm
npm install -g pnpm

# Install all dependencies
pnpm install
```

### 2. Working on a Module

```bash
# Run specific module in dev mode
pnpm --filter @isrms/security-risk-analysis dev

# Run dashboard
pnpm --filter @isrms/dashboard dev

# Run all in parallel
pnpm dev
```

### 3. Adding New Functionality

#### If it's shared across modules:
→ Add to `packages/core`

#### If it's data handling:
→ Add to `packages/data-layer`

#### If it's module-specific:
→ Add to respective module package

### 4. Testing

```bash
# Run all tests
pnpm test

# Run tests for specific package
pnpm --filter @isrms/core test

# Watch mode
pnpm --filter @isrms/core test:watch
```

## Code Standards

### TypeScript
- Use strict mode
- Define explicit types (avoid `any`)
- Use interfaces for data structures
- Use enums for fixed constants

### Python
- Type hints required
- Follow PEP 8
- Use dataclasses for structured data

### Imports
```typescript
// Use workspace aliases
import { RiskLevel } from '@isrms/core/types';
import { calculateASHER } from '@isrms/core/calculations';
```

## Migration Checklist

When migrating existing code:

- [ ] Extract shared utilities to `@isrms/core`
- [ ] Standardize terminology (see terminology.md)
- [ ] Move data parsing to `@isrms/data-layer`
- [ ] Add TypeScript types
- [ ] Write unit tests
- [ ] Update documentation
- [ ] Add to module's README

## Git Workflow

### Branch Naming
- Features: `feature/asher-system-level`
- Fixes: `fix/nibrs-calculation`
- Docs: `docs/api-reference`

### Commit Messages
```
feat(core): add system-level ASHER calculation
fix(data-layer): handle OCR errors in watch logs
docs(terminology): standardize risk level definitions
```

### Pull Requests
1. Create feature branch
2. Make changes
3. Write tests
4. Update docs
5. Submit PR with description
6. Request review
7. Merge after approval

## Common Tasks

### Adding a New Risk Calculator

1. Define types in `packages/core/src/types/`
2. Implement calculation in `packages/core/src/calculations/`
3. Add tests in `packages/core/tests/`
4. Use in module via import

### Adding a New Datasheet Parser

1. Create parser in `packages/data-layer/src/parsers/`
2. Add validation schema
3. Register in InputManager
4. Add tests
5. Document expected format

### Creating a New Dashboard Component

1. Add to `apps/dashboard/src/components/`
2. Import required data hooks
3. Use shared types from `@isrms/core`
4. Add to appropriate page
5. Style with Tailwind

## Troubleshooting

### "Cannot find module '@isrms/core'"
```bash
pnpm install
```

### TypeScript errors after changes
```bash
pnpm --filter @isrms/core build
```

### Tests failing after migration
Ensure imports use workspace aliases, not relative paths
