/**
 * Query keys for gear module - consistent cache management with TanStack Query
 */
export const gearQueryKeys = {
  all: ['gear'] as const,
  
  // All items queries
  items: () => [...gearQueryKeys.all, 'items'] as const,
  item: (id: string) => [...gearQueryKeys.items(), id] as const,
  
  // Containers queries  
  containers: () => [...gearQueryKeys.all, 'containers'] as const,
  container: (id: string) => [...gearQueryKeys.containers(), id] as const,
  
  // Children queries (items in a container)
  children: (parentId: string) => [...gearQueryKeys.all, 'children', parentId] as const,
  
  // Filtered queries
  itemsFiltered: (filters: Record<string, unknown>) => [...gearQueryKeys.items(), filters] as const,
} as const
