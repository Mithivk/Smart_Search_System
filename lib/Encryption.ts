import CryptoJS from 'crypto-js';

const secretKey = process.env.ENCRYPTION_KEY;

if (!secretKey) {
  throw new Error('ENCRYPTION_KEY environment variable is required');
}

// Optional: Add a pepper for additional security
const pepper = process.env.ENCRYPTION_PEPPER || '';

/**
 * Enhanced encryption with optional pepper
 */
export function encryptData(data: string): string {
  try {
    if (!data) {
      throw new Error('Cannot encrypt empty data');
    }
    
    // Add pepper if provided (additional security measure)
    const dataToEncrypt = pepper ? `${data}${pepper}` : data;
    const encrypted = CryptoJS.AES.encrypt(dataToEncrypt, secretKey).toString();
    
    if (!encrypted) {
      throw new Error('Encryption returned empty result');
    }
    
    return encrypted;
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt data');
  }
}

/**
 * Enhanced decryption with optional pepper removal
 */
export function decryptData(encryptedData: string): string {
  try {
    if (!encryptedData) {
      throw new Error('Cannot decrypt empty data');
    }
    
    const bytes = CryptoJS.AES.decrypt(encryptedData, secretKey);
    let decrypted = bytes.toString(CryptoJS.enc.Utf8);
    
    if (!decrypted) {
      throw new Error('Decryption failed - empty result');
    }
    
    // Remove pepper if it was added during encryption
    if (pepper && decrypted.endsWith(pepper)) {
      decrypted = decrypted.slice(0, -pepper.length);
    }
    
    return decrypted;
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error('Failed to decrypt data');
  }
}