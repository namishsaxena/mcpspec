---
description: Testing standards and TDD practices
alwaysApply: true
---

# Testing Rules

## TDD Cycle

1. **Red**: Write a failing test that describes the behavior you want.
2. **Green**: Write the minimal implementation to make the test pass.
3. **Refactor**: Clean up without changing behavior. Tests stay green.

## Test Structure

- Use **Arrange-Act-Assert** (AAA) in every test:
  - **Arrange**: Set up the test data and preconditions.
  - **Act**: Call the function or trigger the behavior being tested.
  - **Assert**: Verify the result matches expectations.

## One Behavior Per Test

- Each test asserts one behavior. If a test fails, the name tells you exactly what broke.
- Multiple assertions are fine if they all verify the same behavior (e.g., checking both status code and body of a response).

## Test Behavior, Not Implementation

- Test what the function does, not how it does it.
- Do NOT assert on internal state, private variables, or call counts (unless testing a mock boundary).

## Mocking Policy

- Prefer real implementations over mocks.
- Mock ONLY at system boundaries: network calls, filesystem, timers.
- Never mock the module under test.

## Fast Feedback

- Run a single test file for fast feedback: `pnpm vitest run tests/<file>.test.ts`
- Full test suite (`pnpm test`) before committing.

## Flaky Tests

- Fix flaky tests immediately. Do not add retries or skip decorators.
- Common causes: shared mutable state, timing dependencies, uncontrolled randomness.

## Descriptive Test Names

- Good: `"filters tools matching exclude patterns"`
- Good: `"returns empty spec when server has no capabilities"`
- Bad: `"test filter"`, `"it works"`, `"test1"`
