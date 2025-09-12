import mongoose from 'mongoose';
import { encryptData, decryptData } from '../lib/Encryption';

const ConfigSchema = new mongoose.Schema({
  userId: {
    type: String,
    required: true,
    unique: true,
    index: true // Add index here instead of separate index() call
  },
  apiKey: {
    type: String,
    required: true
  },
  environment: {
    type: String,
    required: true,
    default: 'production'
  },
  accessToken: {
    type: String,
    required: true
  }
}, {
  timestamps: true
});

// Remove the separate index() call to avoid duplicate index warning
// ConfigSchema.index({ userId: 1 }); // REMOVE THIS LINE

// Add pre-save middleware to handle encryption
ConfigSchema.pre('save', function(next) {
  if (this.isModified('apiKey')) {
    this.apiKey = encryptData(this.apiKey);
  }
  if (this.isModified('accessToken')) {
    this.accessToken = encryptData(this.accessToken);
  }
  next();
});

// Add post-find middleware to handle decryption
ConfigSchema.post('find', function(docs) {
  docs.forEach((doc: any) => {
    if (doc.apiKey) doc.apiKey = decryptData(doc.apiKey);
    if (doc.accessToken) doc.accessToken = decryptData(doc.accessToken);
  });
});

ConfigSchema.post('findOne', function(doc) {
  if (doc) {
    if (doc.apiKey) doc.apiKey = decryptData(doc.apiKey);
    if (doc.accessToken) doc.accessToken = decryptData(doc.accessToken);
  }
});

// Remove getters/setters since we're using middleware
// This avoids issues with mongoose getters/setters

export default mongoose.models.Config || mongoose.model('Config', ConfigSchema);