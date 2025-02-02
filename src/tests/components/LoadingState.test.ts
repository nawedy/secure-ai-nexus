import { render } from '@testing-library/svelte';
import LoadingState from '$lib/components/LoadingState.svelte';
import { vi } from 'vitest';

describe('LoadingState', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('shows spinner by default', async () => {
    const { container } = render(LoadingState);
    vi.advanceTimersByTime(200);
    expect(container.querySelector('.spinner')).toBeInTheDocument();
  });

  it('shows skeleton loader when type is skeleton', async () => {
    const { container } = render(LoadingState, {
      props: { type: 'skeleton' }
    });
    vi.advanceTimersByTime(200);
    expect(container.querySelector('.skeleton-loader')).toBeInTheDocument();
  });

  it('shows progress bar with correct width', async () => {
    const { container } = render(LoadingState, {
      props: {
        type: 'progress',
        progress: 50
      }
    });
    vi.advanceTimersByTime(200);
    const progressBar = container.querySelector('.progress');
    expect(progressBar).toHaveStyle({ width: '50%' });
  });

  it('shows loading text when provided', async () => {
    const { getByText } = render(LoadingState, {
      props: { text: 'Loading...' }
    });
    vi.advanceTimersByTime(200);
    expect(getByText('Loading...')).toBeInTheDocument();
  });
});
