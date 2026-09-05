/**
 * Ultra-Enterprise Models Architecture (V3 - Absolute User Data Isolation)
 * Designed for Telegram Mini Apps & Shortener Engines
 * Ensures 100% Multi-Tenant Isolation, Zero-Data-Leakage, & High Index Performance
 */

if (typeof window !== 'undefined') {
  throw new Error("Critical Security Alert: Mongoose models must run exclusively on the server side.");
}

const mongoose = require('mongoose');

// Precision currency formatter up to 5 decimal places (Prevents JS Floating-point flaws)
const formatCurrency = (val) => {
  if (typeof val !== 'number' || isNaN(val) || !isFinite(val)) return 0;
  return Math.round((val + Number.EPSILON) * 100000) / 100000;
};

// --------------------------------------------------
// 1. User Model (Isolated Profiles, Balances & Stats)
// --------------------------------------------------
const userSchema = new mongoose.Schema({
  telegramId: { 
    type: String, 
    required: [true, 'Telegram ID is required'], 
    unique: true, 
    index: true,
    trim: true 
  },
  username: { 
    type: String, 
    default: '', 
    trim: true,
    lowercase: true 
  },
  language: {
    type: String,
    default: 'ar',
    trim: true,
    lowercase: true
  },
  role: { 
    type: String, 
    enum: ['user', 'admin'], 
    default: 'user',
    index: true 
  },
  pendingBalance: { 
    type: Number, 
    default: 0, 
    min: [0, 'Pending balance cannot be negative'],
    set: formatCurrency 
  },
  availableBalance: { 
    type: Number, 
    default: 0, 
    min: [0, 'Available balance cannot be negative'],
    set: formatCurrency 
  },
  isBanned: { 
    type: Boolean, 
    default: false, 
    index: true 
  },
  referredBy: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    default: null, 
    index: true 
  },
  referralEarnings: { 
    type: Number, 
    default: 0, 
    min: 0,
    set: formatCurrency 
  },
  defaultWallet: { 
    type: String, 
    default: '', 
    trim: true,
    validate: {
      validator: function(v) {
        if (!v || v === '') return true;
        const isTron = /^T[A-Za-z1-9]{33}$/.test(v);
        const isEvm = /^0x[a-fA-F0-9]{40}$/.test(v);
        const isTon = /^[a-zA-Z0-9_-]{48}$/.test(v) || /^0:[a-fA-F0-9]{64}$/.test(v);
        return isTron || isEvm || isTon;
      },
      message: 'Invalid wallet address format (Must be USDT TRC20, BEP20/ERC20, or TON)'
    }
  },
  statsSummary: {
    totalLinksCreated: { type: Number, default: 0, min: 0 },
    totalViewsReceived: { type: Number, default: 0, min: 0 },
    totalValidViews: { type: Number, default: 0, min: 0 },
    totalLifetimeEarned: { type: Number, default: 0, min: 0, set: formatCurrency }
  }
}, { 
  timestamps: true,
  versionKey: '__v'
});

userSchema.index({ telegramId: 1, isBanned: 1 });

userSchema.methods.toPrivateJSON = function() {
  const obj = this.toObject();
  delete obj.__v;
  return obj;
};

// --------------------------------------------------
// 2. Self-Serve Ad Model (Advertiser Specific Data)
// --------------------------------------------------
const adSchema = new mongoose.Schema({
  advertiserId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: [true, 'Advertiser ID is required'], 
    index: true 
  },
  title: { 
    type: String, 
    required: [true, 'Ad title is required'], 
    trim: true, 
    maxlength: [100, 'Ad title must not exceed 100 characters'] 
  },
  targetUrl: { 
    type: String, 
    required: [true, 'Target URL is required'], 
    trim: true,
    validate: {
      validator: function(v) {
        return /^(https?:\/\/)?([\w.-]+)+[\w\-_~:/?#[\]@!$&'()*+,;=.]+$/i.test(v);
      },
      message: 'Please enter a valid target URL'
    }
  },
  totalBudget: { 
    type: Number, 
    required: [true, 'Total budget is required'], 
    min: [5, 'Minimum campaign budget is $5'], 
    set: formatCurrency 
  },
  remainingBudget: { 
    type: Number, 
    required: true, 
    min: [0, 'Remaining budget cannot be negative'], 
    set: formatCurrency 
  },
  cpmRate: { 
    type: Number, 
    default: 1.50,
    min: 0,
    set: formatCurrency
  },
  costPerImpression: { 
    type: Number, 
    default: 0.0015,
    min: 0,
    set: formatCurrency
  },
  publisherEarningsPerImpression: {
    type: Number,
    default: 0.00135,
    min: 0,
    set: formatCurrency
  },
  platformFeePerImpression: {
    type: Number,
    default: 0.00015,
    min: 0,
    set: formatCurrency
  },
  impressionsCount: { 
    type: Number, 
    default: 0, 
    min: 0 
  },
  status: { 
    type: String, 
    enum: ['active', 'paused', 'completed'], 
    default: 'active', 
    index: true 
  }
}, { 
  timestamps: true 
});

adSchema.index({ advertiserId: 1, status: 1, createdAt: -1 });
adSchema.index({ status: 1, remainingBudget: 1, createdAt: -1 });

// --------------------------------------------------
// 3. Shortened Link Model (Strictly Isolated Publisher Data)
// --------------------------------------------------
const linkSchema = new mongoose.Schema({
  shortCode: { 
    type: String, 
    required: true, 
    unique: true, 
    index: true,
    trim: true 
  },
  userId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: [true, 'Owner User ID is required for strict isolation'], 
    index: true 
  },
  title: { 
    type: String, 
    default: 'Untitled Link', 
    trim: true,
    maxlength: 150 
  },
  targetUrl: { 
    type: String, 
    required: true, 
    trim: true 
  },
  isActive: { 
    type: Boolean, 
    default: true, 
    index: true 
  },
  views: { 
    type: Number, 
    default: 0, 
    min: 0 
  },
  validImpressions: { 
    type: Number, 
    default: 0, 
    min: 0 
  },
  invalidImpressions: { 
    type: Number, 
    default: 0, 
    min: 0 
  }
}, { 
  timestamps: true 
});

// Compound Indexes for Zero Leakage Performance
linkSchema.index({ userId: 1, createdAt: -1 });
linkSchema.index({ userId: 1, isActive: 1, createdAt: -1 });
linkSchema.index({ userId: 1, shortCode: 1 });

/**
 * STATIC METHOD: Enforce Isolated Fetching
 * تضمن هذه الدالة عدم إمكانية جلب أي روابط بدون دمج userId الخص بالمستخدم بشكل إجباري
 */
linkSchema.statics.getUserIsolatedLinks = function(userId, query = {}, options = {}) {
  if (!userId) {
    throw new Error("Security Violation: userId is required to fetch links.");
  }
  const safeQuery = { ...query, userId: userId };
  return this.find(safeQuery, null, options).sort({ createdAt: -1 });
};

// --------------------------------------------------
// 4. Traffic & Impressions Model
// --------------------------------------------------
const impressionSchema = new mongoose.Schema({
  linkId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Link', 
    required: true, 
    index: true 
  },
  publisherId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  viewerTelegramId: {
    type: String,
    default: null,
    trim: true,
    index: true
  },
  adSource: { 
    type: String, 
    enum: ['internal', 'adsgram'], 
    default: 'adsgram',
    index: true
  },
  adId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Ad', 
    default: null,
    index: true
  },
  publisherEarnings: {
    type: Number,
    default: 0.00135,
    set: formatCurrency
  },
  ip: { 
    type: String, 
    required: true, 
    trim: true 
  },
  userAgent: { 
    type: String, 
    default: '', 
    trim: true 
  },
  isUnique: { 
    type: Boolean, 
    default: true 
  },
  createdAt: { 
    type: Date, 
    default: Date.now, 
    expires: '60d' 
  }
});

impressionSchema.index({ publisherId: 1, createdAt: -1 });
impressionSchema.index({ linkId: 1, publisherId: 1, createdAt: -1 });
impressionSchema.index({ ip: 1, linkId: 1, createdAt: -1 });

// --------------------------------------------------
// 5. Anti-Bypass Click Session Model
// --------------------------------------------------
const clickSessionSchema = new mongoose.Schema({
  linkId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Link', 
    required: true 
  },
  visitorTelegramId: { 
    type: String, 
    default: null, 
    trim: true,
    index: true 
  },
  adSource: { 
    type: String, 
    enum: ['internal', 'adsgram'], 
    default: 'adsgram'
  },
  adId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Ad', 
    default: null 
  },
  ip: { 
    type: String, 
    required: true, 
    trim: true 
  },
  bridgeToken: { 
    type: String, 
    required: true,
    trim: true 
  },
  createdAt: { 
    type: Date, 
    default: Date.now, 
    expires: 300 
  }
});

clickSessionSchema.index({ linkId: 1, ip: 1 });
clickSessionSchema.index({ bridgeToken: 1 }, { unique: true });

// --------------------------------------------------
// 6. Withdraw Request Model
// --------------------------------------------------
const withdrawSchema = new mongoose.Schema({
  userId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: [true, 'User ID is required'], 
    index: true 
  },
  amount: { 
    type: Number, 
    required: [true, 'Total withdrawal amount is required'], 
    min: [30, 'Minimum withdrawal limit is $30'],
    set: formatCurrency 
  },
  fee: {
    type: Number,
    default: 3,
    set: formatCurrency
  },
  netAmount: {
    type: Number,
    required: true,
    set: formatCurrency
  },
  network: {
    type: String,
    enum: ['BEP20', 'TRC20', 'TON'],
    required: [true, 'Please select network (BEP20, TRC20, or TON)'],
    trim: true,
    uppercase: true
  },
  walletAddress: { 
    type: String, 
    required: [true, 'Wallet address is required'], 
    trim: true 
  },
  status: { 
    type: String, 
    enum: ['pending', 'approved', 'rejected'], 
    default: 'pending', 
    lowercase: true,
    index: true 
  },
  rejectReason: { 
    type: String, 
    default: '', 
    trim: true 
  },
  note: { 
    type: String, 
    default: '', 
    trim: true 
  }
}, { 
  timestamps: true 
});

withdrawSchema.pre('validate', function(next) {
  const amount = typeof this.amount === 'number' ? this.amount : 0;
  const fee = typeof this.fee === 'number' ? this.fee : 3;
  this.netAmount = formatCurrency(Math.max(0, amount - fee));
  next();
});

withdrawSchema.index({ userId: 1, status: 1, createdAt: -1 });

// --------------------------------------------------
// 7. Earnings Hold Model
// --------------------------------------------------
const earningsHoldSchema = new mongoose.Schema({
  userId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'User', 
    required: true, 
    index: true 
  },
  amount: { 
    type: Number, 
    required: true, 
    min: 0,
    set: formatCurrency 
  },
  releaseAt: { 
    type: Date, 
    required: true, 
    default: () => new Date(Date.now() + 24 * 60 * 60 * 1000),
    index: true 
  },
  isReleased: { 
    type: Boolean, 
    default: false, 
    index: true 
  }
}, { 
  timestamps: true 
});

earningsHoldSchema.index({ userId: 1, isReleased: 1, releaseAt: 1 });

// --------------------------------------------------
// 8. Advertiser Deposit Model
// --------------------------------------------------
const depositSchema = new mongoose.Schema({
  advertiserId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Advertiser ID is required'],
    index: true
  },
  amount: {
    type: Number,
    required: [true, 'Deposit amount is required'],
    min: [1, 'Minimum deposit limit is $1'],
    set: formatCurrency
  },
  network: {
    type: String,
    enum: ['BEP20', 'TRC20', 'TON'],
    required: [true, 'Please select network (BEP20, TRC20, TON)'],
    trim: true,
    uppercase: true
  },
  txid: {
    type: String,
    required: [true, 'Transaction hash (TxID) is required'],
    trim: true,
    unique: true
  },
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending',
    lowercase: true,
    index: true
  },
  rejectReason: {
    type: String,
    default: '',
    trim: true
  }
}, { timestamps: true });

depositSchema.index({ advertiserId: 1, status: 1, createdAt: -1 });

// --------------------------------------------------
// 9. Announcement Model
// --------------------------------------------------
const announcementSchema = new mongoose.Schema({
  title: { type: String, required: true, trim: true },
  content: { type: String, required: true, trim: true },
  isActive: { type: Boolean, default: true, index: true },
  targetUser: { type: mongoose.Schema.Types.ObjectId, ref: 'User', default: null, index: true }
}, { timestamps: true });

announcementSchema.index({ isActive: 1, targetUser: 1, createdAt: -1 });

// Exporting Optimized Safe Models
const User = mongoose.models.User || mongoose.model('User', userSchema);
const Ad = mongoose.models.Ad || mongoose.model('Ad', adSchema);
const Link = mongoose.models.Link || mongoose.model('Link', linkSchema);
const Impression = mongoose.models.Impression || mongoose.model('Impression', impressionSchema);
const ClickSession = mongoose.models.ClickSession || mongoose.model('ClickSession', clickSessionSchema);
const Withdraw = mongoose.models.Withdraw || mongoose.model('Withdraw', withdrawSchema);
const EarningsHold = mongoose.models.EarningsHold || mongoose.model('EarningsHold', earningsHoldSchema);
const Deposit = mongoose.models.Deposit || mongoose.model('Deposit', depositSchema);
const Announcement = mongoose.models.Announcement || mongoose.model('Announcement', announcementSchema);

module.exports = {
  User,
  Ad,
  Link,
  Impression,
  ClickSession,
  Withdraw,
  EarningsHold,
  Deposit,
  Announcement
};
