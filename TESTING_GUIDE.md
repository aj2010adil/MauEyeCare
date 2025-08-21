# MauEyeCare Testing Guide

This guide covers all aspects of testing the MauEyeCare application, including unit tests, integration tests, and end-to-end testing.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Types](#test-types)
5. [Writing Tests](#writing-tests)
6. [Test Coverage](#test-coverage)
7. [Continuous Integration](#continuous-integration)
8. [Troubleshooting](#troubleshooting)

## 🎯 Overview

MauEyeCare uses a comprehensive testing strategy with:
- **Unit Tests**: React components and utility functions
- **Integration Tests**: API endpoints and database operations
- **End-to-End Tests**: Complete user workflows
- **Performance Tests**: Load and stress testing

## 📁 Test Structure

```
tests/
├── setup.ts                    # Test configuration and mocks
├── test_integration.py         # Python integration tests
└── test_components.test.tsx    # React component tests

vitest.config.ts               # Vitest configuration
```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
npm run test:e2e

# Run unit tests only
npm run test

# Run integration tests only
npm run test:integration

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

### Using PowerShell Script

```powershell
# Run all tests
.\scripts\run-tests.ps1

# Run specific test types
.\scripts\run-tests.ps1 -TestType unit
.\scripts\run-tests.ps1 -TestType integration
.\scripts\run-tests.ps1 -TestType e2e

# Run with coverage
.\scripts\run-tests.ps1 -Coverage

# Run in watch mode
.\scripts\run-tests.ps1 -Watch
```

## 🧪 Test Types

### 1. Unit Tests (React Components)

**Location**: `tests/test_components.test.tsx`

**Purpose**: Test individual React components in isolation

**Coverage**:
- Component rendering
- User interactions
- Props handling
- State management
- Event handlers

**Example**:
```typescript
describe('PrescriptionTable', () => {
  it('renders prescription table correctly', () => {
    render(<PrescriptionTable {...mockProps} />)
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })
})
```

### 2. Integration Tests (API)

**Location**: `tests/test_integration.py`

**Purpose**: Test API endpoints and database operations

**Coverage**:
- API endpoints
- Database queries
- Authentication
- Error handling
- Data validation

**Example**:
```python
async def test_patient_workflow(self, client: httpx.AsyncClient, auth_token: str):
    # Create patient
    response = await client.post("/api/patients", json=patient_data)
    assert response.status_code == 200
    
    # Create prescription
    response = await client.post("/api/prescriptions", json=prescription_data)
    assert response.status_code == 200
```

### 3. End-to-End Tests

**Purpose**: Test complete user workflows

**Coverage**:
- Complete doctor workflow
- Patient consultation
- Prescription creation
- Export functionality
- Inventory management

## ✍️ Writing Tests

### React Component Tests

1. **Setup**:
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'

// Mock data
const mockProps = {
  // ... props
}

// Mock functions
const mockOnClick = vi.fn()
```

2. **Test Structure**:
```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    render(<Component {...mockProps} />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('should handle user interactions', () => {
    render(<Component {...mockProps} onClick={mockOnClick} />)
    fireEvent.click(screen.getByRole('button'))
    expect(mockOnClick).toHaveBeenCalled()
  })
})
```

### API Integration Tests

1. **Setup**:
```python
import pytest
import httpx
from typing import AsyncGenerator

class TestAPI:
    @pytest.fixture
    async def client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        async with httpx.AsyncClient() as client:
            yield client
```

2. **Test Structure**:
```python
async def test_endpoint(self, client: httpx.AsyncClient):
    response = await client.get("/api/endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## 📊 Test Coverage

### Coverage Reports

```bash
# Generate coverage report
npm run test:coverage

# View coverage in browser
open coverage/index.html
```

### Coverage Targets

- **Statements**: 80%
- **Branches**: 75%
- **Functions**: 80%
- **Lines**: 80%

### Coverage Exclusions

- Test files
- Configuration files
- Build artifacts
- Mock data

## 🔄 Continuous Integration

### GitHub Actions (Recommended)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        npm install
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        .\.venv\Scripts\Activate.ps1
        npm run test:e2e
```

### Local CI

```powershell
# Run full test suite
.\scripts\run-tests.ps1 -TestType all -Coverage

# Check for linting issues
npm run lint

# Build application
npm run build
```

## 🐛 Troubleshooting

### Common Issues

1. **Tests failing due to missing dependencies**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Backend server not starting**
   ```bash
   # Check if port 8000 is available
   netstat -an | findstr :8000
   
   # Kill existing processes
   taskkill /f /im python.exe
   ```

3. **Database connection issues**
   ```bash
   # Check PostgreSQL status
   pg_ctl status -D /path/to/data
   
   # Restart PostgreSQL
   pg_ctl restart -D /path/to/data
   ```

4. **Test environment issues**
   ```bash
   # Clear test cache
   npm run test -- --clearCache
   
   # Reset database
   python scripts/reset_db.py
   ```

### Debug Mode

```bash
# Run tests with verbose output
npm run test -- --verbose

# Run specific test file
npm run test tests/test_components.test.tsx

# Run tests in watch mode
npm run test -- --watch
```

### Performance Testing

```bash
# Run performance tests
python -m pytest tests/test_integration.py::TestPerformance -v

# Load testing
python scripts/load_test.py
```

## 📈 Best Practices

### 1. Test Organization

- Group related tests in describe blocks
- Use descriptive test names
- Keep tests independent
- Clean up after each test

### 2. Mocking

- Mock external dependencies
- Use realistic mock data
- Avoid over-mocking
- Test error scenarios

### 3. Assertions

- Use specific assertions
- Test both success and failure cases
- Verify side effects
- Check data integrity

### 4. Performance

- Keep tests fast
- Use efficient queries
- Avoid unnecessary setup
- Parallelize when possible

## 🔧 Test Configuration

### Vitest Configuration

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html']
    }
  }
})
```

### Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## 📚 Additional Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this guide if needed

## 📞 Support

For testing-related issues:

1. Check this guide first
2. Review existing test examples
3. Check the troubleshooting section
4. Create an issue with detailed information
