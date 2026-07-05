import type { IGearContainer } from '../types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Check if a container is nested (has a parent)
 */
export function isNestedContainer(container: IGearContainer): boolean {
  return !!container.parentContainerId
}

/**
 * Get the depth of a container in the hierarchy (0 = root, 1 = first level nested, etc.)
 */
export function getContainerDepth(containerId: TUUID, containers: IGearContainer[]): number {
  const container = containers.find(c => c.id === containerId)
  if (!container || !container.parentContainerId) {
    return 0
  }

  return 1 + getContainerDepth(container.parentContainerId, containers)
}

/**
 * Get the path from root to the specified container (breadcrumb path)
 */
export function getContainerPath(containerId: TUUID, containers: IGearContainer[]): IGearContainer[] {
  const container = containers.find(c => c.id === containerId)
  if (!container) {
    return []
  }

  if (!container.parentContainerId) {
    return [container]
  }

  const parentPath = getContainerPath(container.parentContainerId, containers)
  return [...parentPath, container]
}

/**
 * Get all containers nested inside the specified container (recursive)
 */
export function getAllNestedContainers(containerId: TUUID, containers: IGearContainer[]): IGearContainer[] {
  const nested: IGearContainer[] = []

  // Find all containers that have this container as parent
  const directChildren = containers.filter(c => c.parentContainerId === containerId)

  for (const child of directChildren) {
    nested.push(child)
    // Recursively get nested containers of this child
    nested.push(...getAllNestedContainers(child.id, containers))
  }

  return nested
}

/**
 * Check if a container is used as an item in any other container
 */
function isContainerUsedAsItem(containerId: TUUID, containers: IGearContainer[]): boolean {
  // Check all containers and their items
  for (const container of containers) {
    // Check if any item in this container references the given container
    if (container.items.some(item => item.containerId === containerId)) {
      return true
    }
  }
  return false
}

/**
 * Get all root containers (containers without parents and not used as items)
 * A container is considered "root" if:
 * - It doesn't have a parentContainerId
 * - It's not used as an item in any other container
 */
export function getRootContainers(containers: IGearContainer[]): IGearContainer[] {
  return containers.filter(c => {
    // Must not have a parent
    if (c.parentContainerId) {
      return false
    }
    // Must not be used as an item in any other container
    return !isContainerUsedAsItem(c.id, containers)
  })
}

/**
 * Check if setting a parent would create a circular reference
 */
export function wouldCreateCircularReference(
  containerId: TUUID,
  potentialParentId: TUUID,
  containers: IGearContainer[]
): boolean {
  // A container cannot be its own parent
  if (containerId === potentialParentId) {
    return true
  }

  // Check if the potential parent is nested inside the container (would create cycle)
  const nestedContainers = getAllNestedContainers(containerId, containers)
  return nestedContainers.some(c => c.id === potentialParentId)
}

