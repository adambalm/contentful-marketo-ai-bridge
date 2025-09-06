import { vi } from 'vitest';

const mockSdk: any = {
  app: {
    onConfigure: vi.fn(),
    getParameters: vi.fn().mockResolvedValue(null),
    setReady: vi.fn(),
    getCurrentState: vi.fn().mockResolvedValue({}),
  },
  ids: {
    app: 'test-app',
  },
  // Provide defaults expected by components
  parameters: {
    installation: { backendUrl: 'http://localhost:8000' },
  },
  entry: {
    getSys: vi.fn(() => ({ id: 'entry-123' })),
  },
  notifier: {
    success: vi.fn(),
    error: vi.fn(),
  },
};

export { mockSdk };
