/**
 * Tests for Architecture Pinia Store (RefMemTree-powered)
 * 
 * Critical tests for RefMemTree frontend integration!
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useArchitectureStore } from 'src/stores/architecture';

vi.mock('src/services/architectureApi', () => ({
  generateArchitecture: vi.fn(),
  createModule: vi.fn(),
  listModules: vi.fn(),
  updateModule: vi.fn(),
  deleteModule: vi.fn(),
  createDependency: vi.fn(),
  listDependencies: vi.fn(),
  deleteDependency: vi.fn(),
  validateArchitecture: vi.fn(),
  getComplexityAnalysis: vi.fn(),
}));

import * as architectureApi from 'src/services/architectureApi';

describe('Architecture Store (RefMemTree)', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  describe('State Management', () => {
    it('should initialize correctly', () => {
      const store = useArchitectureStore();

      expect(store.modules).toEqual([]);
      expect(store.dependencies).toEqual([]);
      expect(store.validation).toBeNull();
      expect(store.complexity).toBeNull();
    });
  });

  describe('generateArchitecture Action (AI + RefMemTree)', () => {
    it('should generate architecture with AI', async () => {
      const store = useArchitectureStore();

      const mockResponse = {
        modules: [
          { id: 'm1', name: 'UserService', module_type: 'service' },
          { id: 'm2', name: 'Database', module_type: 'database' },
        ],
        dependencies: [
          { id: 'd1', from_module_id: 'm1', to_module_id: 'm2', dependency_type: 'uses' },
        ],
        rules: [],
        overall_score: 8.5,
      };

      vi.mocked(architectureApi.generateArchitecture).mockResolvedValue(mockResponse);

      const result = await store.generateArchitecture('project-1', {
        project_id: 'project-1',
      });

      expect(result).toEqual(mockResponse);
      expect(store.modules).toEqual(mockResponse.modules);
      expect(store.dependencies).toEqual(mockResponse.dependencies);
    });
  });

  describe('RefMemTree-Powered Operations', () => {
    it('should validate architecture using RefMemTree', async () => {
      const store = useArchitectureStore();

      const mockValidation = {
        is_valid: false,
        issues: [
          {
            type: 'circular_dependency',
            severity: 'critical',
            message: 'Circular dependency detected',
            affected_modules: ['m1', 'm2'],
          },
        ],
        errors_count: 1,
        warnings_count: 0,
      };

      vi.mocked(architectureApi.validateArchitecture).mockResolvedValue(mockValidation);

      await store.validateArchitecture('project-1');

      expect(store.validation).toEqual(mockValidation);
      expect(store.validation?.is_valid).toBe(false);
      expect(store.validation?.errors_count).toBe(1);
    });

    it('should analyze complexity with RefMemTree', async () => {
      const store = useArchitectureStore();

      const mockComplexity = {
        overall_complexity: 7.5,
        metrics: {
          module_count: 10,
          avg_dependencies: 3.2,
          max_depth: 4,
          cyclomatic_complexity: 42,
          coupling_score: 6.5,
          cohesion_score: 7.8,
        },
        hotspots: [
          {
            module_id: 'm1',
            module_name: 'CoreEngine',
            complexity_score: 9.2,
            reason: 'Too many dependencies',
          },
        ],
        recommendations: ['Split CoreEngine into smaller modules'],
      };

      vi.mocked(architectureApi.getComplexityAnalysis).mockResolvedValue(mockComplexity);

      await store.analyzeComplexity('project-1');

      expect(store.complexity).toEqual(mockComplexity);
      expect(store.complexity?.overall_complexity).toBe(7.5);
      expect(store.complexity?.hotspots.length).toBe(1);
    });
  });

  describe('Module Management with RefMemTree Sync', () => {
    it('should create module and sync to RefMemTree', async () => {
      const store = useArchitectureStore();

      const newModule = {
        id: 'new-m1',
        project_id: 'p1',
        name: 'NewService',
        module_type: 'service',
        level: 0,
        status: 'draft',
      };

      vi.mocked(architectureApi.createModule).mockResolvedValue(newModule);

      const result = await store.createModule({
        project_id: 'p1',
        name: 'NewService',
        module_type: 'service',
      });

      expect(result).toEqual(newModule);
      expect(store.modules).toContain(newModule);
    });

    it('should update module and maintain consistency', async () => {
      const store = useArchitectureStore();

      store.modules = [
        { id: 'm1', name: 'OldName', module_type: 'service', status: 'draft' },
      ];

      const updated = { id: 'm1', name: 'NewName', module_type: 'service', status: 'approved' };

      vi.mocked(architectureApi.updateModule).mockResolvedValue(updated);

      await store.updateModule('m1', { name: 'NewName' });

      expect(store.modules[0].name).toBe('NewName');
      expect(store.modules[0].status).toBe('approved');
    });

    it('should delete module and remove from state', async () => {
      const store = useArchitectureStore();

      store.modules = [
        { id: 'm1', name: 'Module1', module_type: 'module' },
        { id: 'm2', name: 'Module2', module_type: 'module' },
      ];

      vi.mocked(architectureApi.deleteModule).mockResolvedValue(undefined);

      await store.deleteModule('m1');

      expect(store.modules.length).toBe(1);
      expect(store.modules[0].id).toBe('m2');
    });
  });

  describe('Dependency Management', () => {
    it('should create dependency', async () => {
      const store = useArchitectureStore();

      const newDep = {
        id: 'd1',
        project_id: 'p1',
        from_module_id: 'm1',
        to_module_id: 'm2',
        dependency_type: 'uses',
      };

      vi.mocked(architectureApi.createDependency).mockResolvedValue(newDep);

      const result = await store.createDependency({
        project_id: 'p1',
        from_module_id: 'm1',
        to_module_id: 'm2',
        dependency_type: 'uses',
      });

      expect(result).toEqual(newDep);
      expect(store.dependencies).toContain(newDep);
    });

    it('should maintain dependency consistency', async () => {
      const store = useArchitectureStore();

      store.dependencies = [{ id: 'd1', from_module_id: 'm1', to_module_id: 'm2' }];

      vi.mocked(architectureApi.deleteDependency).mockResolvedValue(undefined);

      await store.deleteDependency('d1');

      expect(store.dependencies.length).toBe(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      const store = useArchitectureStore();

      vi.mocked(architectureApi.listModules).mockRejectedValue(
        new Error('Network error')
      );

      await store.fetchModules('project-1');

      expect(store.error).toContain('Failed to fetch modules');
      expect(store.modules).toEqual([]); // State unchanged
    });

    it('should clear error on successful operation', async () => {
      const store = useArchitectureStore();

      store.error = 'Previous error';

      vi.mocked(architectureApi.listModules).mockResolvedValue([]);

      await store.fetchModules('project-1');

      expect(store.error).toBeNull(); // Error cleared
    });
  });

  describe('State Consistency', () => {
    it('should keep modules and dependencies in sync', async () => {
      const store = useArchitectureStore();

      // Load modules
      vi.mocked(architectureApi.listModules).mockResolvedValue([
        { id: 'm1', name: 'Module1' },
      ]);

      await store.fetchModules('p1');

      // Load dependencies
      vi.mocked(architectureApi.listDependencies).mockResolvedValue([
        { id: 'd1', from_module_id: 'm1', to_module_id: 'm2' },
      ]);

      await store.fetchDependencies('p1');

      expect(store.modules.length).toBe(1);
      expect(store.dependencies.length).toBe(1);

      // Clear should reset both
      store.clear();

      expect(store.modules.length).toBe(0);
      expect(store.dependencies.length).toBe(0);
    });
  });
});
