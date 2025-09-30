/**
 * Tests for price formatting utilities
 */
import { describe, it, expect } from 'vitest';
import { formatPrice, kopecksToTenge, tengeToKopecks, parsePrice, calculateDeliveryCost } from './price';

describe('formatPrice', () => {
  it('formats kopecks to tenge with thousand separators', () => {
    expect(formatPrice(1200000)).toBe('12 000 ₸');
  });

  it('handles zero correctly', () => {
    expect(formatPrice(0)).toBe('0 ₸');
  });

  it('handles large numbers', () => {
    expect(formatPrice(1500000000)).toBe('15 000 000 ₸');
  });

  it('formats without symbol when specified', () => {
    expect(formatPrice(1200000, false)).toBe('12 000');
  });
});

describe('kopecksToTenge', () => {
  it('converts kopecks to tenge', () => {
    expect(kopecksToTenge(1200000)).toBe(12000);
  });

  it('handles zero', () => {
    expect(kopecksToTenge(0)).toBe(0);
  });

  it('rounds to nearest tenge', () => {
    expect(kopecksToTenge(12345)).toBe(123);
  });
});

describe('tengeToKopecks', () => {
  it('converts tenge to kopecks', () => {
    expect(tengeToKopecks(12000)).toBe(1200000);
  });

  it('handles zero', () => {
    expect(tengeToKopecks(0)).toBe(0);
  });
});

describe('parsePrice', () => {
  it('parses formatted price string to kopecks', () => {
    expect(parsePrice('12 000 ₸')).toBe(1200000);
  });

  it('handles plain numbers', () => {
    expect(parsePrice('1500')).toBe(150000);
  });

  it('removes all non-digit characters', () => {
    expect(parsePrice('7 900 ₸')).toBe(790000);
  });
});

describe('calculateDeliveryCost', () => {
  it('charges delivery for orders below threshold', () => {
    expect(calculateDeliveryCost(1000000)).toBe(150000);
  });

  it('provides free delivery at threshold', () => {
    expect(calculateDeliveryCost(1500000)).toBe(0);
  });

  it('provides free delivery above threshold', () => {
    expect(calculateDeliveryCost(2000000)).toBe(0);
  });
});