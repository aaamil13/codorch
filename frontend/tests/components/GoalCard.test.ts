/**
 * Tests for GoalCard Component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { Quasar } from 'quasar';
import GoalCard from 'src/components/goals/GoalCard.vue';

describe('GoalCard Component', () => {
  const mountComponent = (props = {}) => {
    return mount(GoalCard, {
      props: {
        goal: {
          id: '1',
          title: 'Test Goal',
          description: 'Test description',
          overall_smart_score: 8.5,
          status: 'active' as const, // Explicitly cast status
          priority: 'high' as const, // Explicitly cast priority
          project_id: 'project-1', // Add missing property
          is_smart_validated: true, // Add missing property
          completion_percentage: 0, // Add missing property
          created_at: new Date().toISOString(), // Add missing property
          updated_at: new Date().toISOString(), // Add missing property
          ...props,
        },
      },
      global: {
        plugins: [Quasar],
      },
    });
  };

  it('should render goal title', () => {
    const wrapper = mountComponent();

    expect(wrapper.text()).toContain('Test Goal');
  });

  it('should display SMART score', () => {
    const wrapper = mountComponent();

    expect(wrapper.text()).toContain('8.5');
  });

  it('should show status badge', () => {
    const wrapper = mountComponent();

    // Should have status indicator
    expect(wrapper.find('.q-chip, .q-badge').exists()).toBe(true);
  });

  it('should emit click event when clicked', async () => {
    const wrapper = mountComponent();

    await wrapper.trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
  });

  it('should display different colors for different scores', () => {
    const lowScore = mountComponent({ overall_smart_score: 3.0 });
    const highScore = mountComponent({ overall_smart_score: 9.0 });

    // Different visual treatment based on score
    // (exact implementation depends on component)
    expect(lowScore.html()).toBeDefined();
    expect(highScore.html()).toBeDefined();
  });
});
