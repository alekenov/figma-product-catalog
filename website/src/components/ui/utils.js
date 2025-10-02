import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility function to merge Tailwind CSS classes
 * Combines clsx for conditional classes and tailwind-merge to resolve conflicts
 *
 * @param {...any} inputs - Class names, objects, or arrays of class names
 * @returns {string} Merged class string
 *
 * @example
 * cn('px-4 py-2', condition && 'bg-primary', { 'text-white': isActive })
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
