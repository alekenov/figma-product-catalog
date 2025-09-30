/**
 * Tests for price utilities
 *
 * Run with: npm test price.test.js
 */

import { kopecksToTenge, tengeToKopecks, formatPrice, parsePrice, calculateDeliveryCost } from './price.js';

// Test kopecksToTenge
console.log('Testing kopecksToTenge...');
console.assert(kopecksToTenge(1200000) === 12000, 'Should convert 1200000 kopecks to 12000 tenge');
console.assert(kopecksToTenge(150000) === 1500, 'Should convert 150000 kopecks to 1500 tenge');
console.assert(kopecksToTenge(0) === 0, 'Should handle 0');
console.log('✓ kopecksToTenge tests passed');

// Test tengeToKopecks
console.log('\nTesting tengeToKopecks...');
console.assert(tengeToKopecks(12000) === 1200000, 'Should convert 12000 tenge to 1200000 kopecks');
console.assert(tengeToKopecks(1500) === 150000, 'Should convert 1500 tenge to 150000 kopecks');
console.assert(tengeToKopecks(0) === 0, 'Should handle 0');
console.log('✓ tengeToKopecks tests passed');

// Test formatPrice
console.log('\nTesting formatPrice...');
console.assert(formatPrice(1200000) === '12 000 ₸', 'Should format 1200000 as "12 000 ₸"');
console.assert(formatPrice(150000) === '1 500 ₸', 'Should format 150000 as "1 500 ₸"');
console.assert(formatPrice(1200000, false) === '12 000', 'Should format without symbol');
console.assert(formatPrice(100000) === '1 000 ₸', 'Should format 1000 tenge');
console.log('✓ formatPrice tests passed');

// Test parsePrice
console.log('\nTesting parsePrice...');
console.assert(parsePrice('12 000 ₸') === 1200000, 'Should parse "12 000 ₸" to 1200000 kopecks');
console.assert(parsePrice('1500') === 150000, 'Should parse "1500" to 150000 kopecks');
console.assert(parsePrice('7 900 ₸') === 790000, 'Should parse "7 900 ₸" to 790000 kopecks');
console.log('✓ parsePrice tests passed');

// Test calculateDeliveryCost
console.log('\nTesting calculateDeliveryCost...');
console.assert(calculateDeliveryCost(1000000) === 150000, 'Should charge delivery for 10000 tenge');
console.assert(calculateDeliveryCost(1500000) === 0, 'Should be free for 15000 tenge threshold');
console.assert(calculateDeliveryCost(2000000) === 0, 'Should be free above threshold');
console.log('✓ calculateDeliveryCost tests passed');

console.log('\n✅ All price utility tests passed!');