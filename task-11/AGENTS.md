# Task 11: Automated Testing Framework Agents

This file defines specialized agents for the Automated Testing Framework project.

## Agents

### TestFrameworkExpert

**Expertise**: Test frameworks, pytest-like patterns, fixtures, parameterization, parallel execution, assertion introspection
**When to invoke**:

- Designing test discovery and runner patterns
- Implementing test fixtures with different scopes (session, module, function)
- Working with parameterized tests
- Debugging assertion introspection and diff display
- Implementing parallel test execution
- Creating custom decorators (@test, @fixture, @skip, @parametrize)
- Optimizing test performance and reporting

**Capabilities**:

- Understand test discovery by naming conventions and decorators
- Implement fixture dependency resolution
- Design parameterization patterns for test data
- Build assertion introspection and detailed error reporting
- Implement parallel worker processes for test execution
- Create rich, colored test output formatting
- Handle test timeouts, skipping, and conditional execution

---

## Quick Start

To invoke the TestFrameworkExpert agent:

```
@TestFrameworkExpert: [your question about the testing framework]
```

Example:

```
@TestFrameworkExpert: How do I add support for fixture teardown and nested fixture dependencies?
```
