// Vitest setup file

import { config } from '@vue/test-utils';
import { Quasar } from 'quasar';

// Configure Quasar for tests
config.global.plugins.push([Quasar, {}]);
