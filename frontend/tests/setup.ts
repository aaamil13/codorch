// Vitest setup file

import { config } from '@vue/test-utils';
import { vi } from 'vitest';

// Mock Quasar's Notify plugin and Quasar itself
vi.mock('quasar', async () => {
  const actual = await vi.importActual('quasar'); // Get actual exports
  return {
    ...actual, // Spread the original module exports
    Notify: {
      create: vi.fn(),
    },
    // If other Quasar components are directly imported and need to be mocked/exposed, list them here
  };
});

// Import Quasar from the mocked module (this will be the mocked version)
import { Quasar } from 'quasar';

// Configure Quasar for tests
config.global.plugins.push([Quasar, {}]);
