import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Utility function to merge Tailwind CSS classes conditionally without conflict.
 * Combines clsx conditional resolution with tailwind-merge rule deduplication.
 *
 * @param inputs Arbitrary number of class strings, objects, arrays, or falsy values.
 * @returns Cleaned and deduplicated single class name string.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}
