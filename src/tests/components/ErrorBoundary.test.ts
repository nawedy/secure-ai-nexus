import { render, fireEvent } from '@testing-library/svelte';
import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';
import { vi } from 'vitest';

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders children when no error', () => {
    const { getByText } = render(ErrorBoundary, {
      slots: {
        default: '<div>Test Content</div>'
      }
    });
    expect(getByText('Test Content')).toBeInTheDocument();
  });

  it('shows error message when error occurs', () => {
    const error = new Error('Test error');
    const { getByText } = render(ErrorBoundary);

    // Simulate error
    window.dispatchEvent(new ErrorEvent('error', { error }));

    expect(getByText('Something went wrong')).toBeInTheDocument();
  });

  it('shows custom fallback message when provided', () => {
    const { getByText } = render(ErrorBoundary, {
      props: {
        fallback: 'Custom error message'
      }
    });

    window.dispatchEvent(new ErrorEvent('error', { error: new Error() }));

    expect(getByText('Custom error message')).toBeInTheDocument();
  });
});
