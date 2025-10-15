/**
 * Phone validation utilities
 * Currently supports Kazakhstan phone numbers (+7XXXXXXXXXX)
 * Can be extended for international formats in the future
 */

export interface PhoneValidationResult {
  isValid: boolean;
  errorMessage?: string;
}

/**
 * Validate Kazakhstan phone number format
 * Expected format: +7XXXXXXXXXX (12 characters total)
 */
export function validateKazakhstanPhone(phone: string): PhoneValidationResult {
  // Remove all spaces and dashes for validation
  const cleaned = phone.replace(/[\s-]/g, '');

  // Empty phone is not valid
  if (!cleaned) {
    return {
      isValid: false,
      errorMessage: 'Введите номер телефона'
    };
  }

  // Check if it starts with +7
  if (!cleaned.startsWith('+7')) {
    return {
      isValid: false,
      errorMessage: 'Номер должен начинаться с +7'
    };
  }

  // Check total length (should be 12: +7 + 10 digits)
  if (cleaned.length < 12) {
    return {
      isValid: false,
      errorMessage: 'Введите номер в формате +7XXXXXXXXXX'
    };
  }

  if (cleaned.length > 12) {
    return {
      isValid: false,
      errorMessage: 'Слишком длинный номер'
    };
  }

  // Check if all characters after +7 are digits
  const digitsAfterPrefix = cleaned.substring(2);
  if (!/^\d{10}$/.test(digitsAfterPrefix)) {
    return {
      isValid: false,
      errorMessage: 'Номер должен содержать только цифры'
    };
  }

  return { isValid: true };
}

/**
 * Filter phone input to allow only valid characters (digits and +)
 * This ensures users can only type valid characters
 */
export function formatPhoneInput(value: string): string {
  // Allow only digits and + sign
  return value.replace(/[^\d+]/g, '');
}

/**
 * Main validation function that can be extended for international formats
 * Currently only supports Kazakhstan
 */
export function validatePhone(phone: string, country: 'KZ' = 'KZ'): PhoneValidationResult {
  switch (country) {
    case 'KZ':
      return validateKazakhstanPhone(phone);
    default:
      return validateKazakhstanPhone(phone);
  }
}
