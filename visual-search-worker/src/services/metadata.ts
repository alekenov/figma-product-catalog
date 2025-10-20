/**
 * Metadata Service
 * Handles product metadata storage and retrieval using D1
 */

import { Env, BouquetMetadata } from '../types';
import { parseJsonArray } from '../utils/validation';

/**
 * Insert or update bouquet metadata in D1
 */
export async function upsertMetadata(
  db: D1Database,
  metadata: {
    product_id: number;
    name: string;
    price: number;
    image_key: string;
    colors?: string[];
    occasions?: string[];
    tags?: string[];
    shop_id?: number;
  }
): Promise<void> {
  try {
    const {
      product_id,
      name,
      price,
      image_key,
      colors,
      occasions,
      tags,
      shop_id = 8,
    } = metadata;

    await db.prepare(`
      INSERT INTO bouquets (
        product_id, name, price, image_key, colors, occasions, tags, shop_id, indexed_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
      ON CONFLICT(product_id) DO UPDATE SET
        name = excluded.name,
        price = excluded.price,
        image_key = excluded.image_key,
        colors = excluded.colors,
        occasions = excluded.occasions,
        tags = excluded.tags,
        shop_id = excluded.shop_id,
        updated_at = datetime('now')
    `)
      .bind(
        product_id,
        name,
        price,
        image_key,
        colors ? JSON.stringify(colors) : null,
        occasions ? JSON.stringify(occasions) : null,
        tags ? JSON.stringify(tags) : null,
        shop_id
      )
      .run();

    console.log(`Upserted metadata for product ${product_id}`);
  } catch (error) {
    console.error('D1 upsert error:', error);
    throw new Error(`Failed to upsert metadata: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get bouquet metadata by product ID
 */
export async function getMetadata(
  db: D1Database,
  productId: number
): Promise<BouquetMetadata | null> {
  try {
    const result = await db.prepare(`
      SELECT * FROM bouquets WHERE product_id = ?
    `)
      .bind(productId)
      .first<BouquetMetadata>();

    return result;
  } catch (error) {
    console.error('D1 get error:', error);
    throw new Error(`Failed to get metadata: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get multiple bouquet metadata by product IDs
 */
export async function getMetadataBatch(
  db: D1Database,
  productIds: number[]
): Promise<Map<number, BouquetMetadata>> {
  if (productIds.length === 0) {
    return new Map();
  }

  try {
    // Create placeholders for IN clause
    const placeholders = productIds.map(() => '?').join(',');
    const query = `SELECT * FROM bouquets WHERE product_id IN (${placeholders})`;

    const result = await db.prepare(query)
      .bind(...productIds)
      .all<BouquetMetadata>();

    // Convert to map for fast lookup
    const map = new Map<number, BouquetMetadata>();
    if (result.results) {
      for (const row of result.results) {
        map.set(row.product_id, row);
      }
    }

    return map;
  } catch (error) {
    console.error('D1 batch get error:', error);
    throw new Error(`Failed to get metadata batch: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Delete bouquet metadata
 */
export async function deleteMetadata(db: D1Database, productId: number): Promise<void> {
  try {
    await db.prepare(`DELETE FROM bouquets WHERE product_id = ?`)
      .bind(productId)
      .run();

    console.log(`Deleted metadata for product ${productId}`);
  } catch (error) {
    console.error('D1 delete error:', error);
    throw new Error(`Failed to delete metadata: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Get total count of indexed bouquets
 */
export async function getTotalCount(db: D1Database, shopId?: number): Promise<number> {
  try {
    const query = shopId
      ? `SELECT COUNT(*) as count FROM bouquets WHERE shop_id = ?`
      : `SELECT COUNT(*) as count FROM bouquets`;

    const result = await db.prepare(query)
      .bind(shopId || undefined)
      .first<{ count: number }>();

    return result?.count || 0;
  } catch (error) {
    console.error('D1 count error:', error);
    return 0;
  }
}

/**
 * Get last indexed timestamp
 */
export async function getLastIndexedAt(db: D1Database): Promise<string | null> {
  try {
    const result = await db.prepare(`
      SELECT indexed_at FROM bouquets ORDER BY indexed_at DESC LIMIT 1
    `)
      .first<{ indexed_at: string }>();

    return result?.indexed_at || null;
  } catch (error) {
    console.error('D1 last indexed error:', error);
    return null;
  }
}

/**
 * Parse metadata arrays (colors, occasions, tags)
 */
export function parseMetadataArrays(metadata: BouquetMetadata): {
  colors?: string[];
  occasions?: string[];
  tags?: string[];
} {
  return {
    colors: parseJsonArray(metadata.colors),
    occasions: parseJsonArray(metadata.occasions),
    tags: parseJsonArray(metadata.tags),
  };
}
