# ✅ Visual Search Webhook Sync - Installation Complete!

**Date:** 2025-10-20
**Status:** 🎉 **FULLY INSTALLED AND READY**

---

## 🚀 What's Been Installed

### 1. ✅ Railway Backend
- **URL:** https://figma-product-catalog-production.up.railway.app
- **Status:** Deployed and healthy
- **Webhook Endpoint:** `POST /api/v1/webhooks/product-sync`
- **Environment Variable:** `WEBHOOK_SECRET=cvety-webhook-2025-secure-key` ✓

### 2. ✅ Cloudflare Visual Search Worker
- **URL:** https://visual-search.alekenov.workers.dev
- **Version:** 9c162d81-04e6-40db-98fb-006c607fc254
- **Endpoint:** `POST /reindex-one`
- **Status:** Deployed successfully

### 3. ✅ Bitrix Event Handler (Production)
- **Location:** `/home/bitrix/www/local/php_interface/init.php`
- **Backup Created:** `init.php.backup-20251020-221707` (23KB)
- **Status:** Installed and active
- **Verification:** Event handlers loaded successfully (confirmed in Apache logs)

**Apache Log Confirmation:**
```
[Mon Oct 20 22:20:05] Railway Visual Search Product Sync handlers loaded successfully
```

---

## 📋 Installed Components

### Bitrix Event Handlers
```php
// Event Handlers
AddEventHandler("iblock", "OnAfterIBlockElementAdd", "syncProductToRailway");
AddEventHandler("iblock", "OnAfterIBlockElementUpdate", "syncProductToRailway");
AddEventHandler("iblock", "OnAfterIBlockElementDelete", "deleteProductFromRailway");
```

### Functions
- `syncProductToRailway($arFields)` - Syncs product create/update to Railway
- `deleteProductFromRailway($arFields)` - Syncs product deletion (soft delete)

### Configuration
- `RAILWAY_WEBHOOK_URL`: https://figma-product-catalog-production.up.railway.app/api/v1/webhooks/product-sync
- `RAILWAY_WEBHOOK_SECRET`: cvety-webhook-2025-secure-key

---

## 🧪 How to Test

### Test 1: Create New Product in Bitrix

**Steps:**
1. Go to Bitrix admin panel: https://cvety.kz/bitrix/admin/
2. Navigate to Products → Add Product
3. Fill in product details:
   - Name: "TEST Visual Search Sync"
   - Price: "5 000 ₸"
   - Upload photo (required for visual search)
   - Height: "60 см"
4. Click "Save"

**What Should Happen:**
1. **Bitrix logs** should show:
   ```
   Railway sync success for product XXXXX
   ```

2. **Railway logs** should show:
   ```
   📨 Received webhook: product.created for product XXXXX
   ✅ Created product XXXXX with 1 images
   ```

3. **Product appears in Railway database:**
   ```bash
   curl "https://figma-product-catalog-production.up.railway.app/api/v1/products/?shop_id=8" | \
     grep "TEST Visual Search Sync"
   ```

4. **Visual Search Worker** indexes the product (background task)

---

### Test 2: Update Product

**Steps:**
1. Edit the test product in Bitrix
2. Change price to "6 000 ₸"
3. Save

**Expected Logs:**
```
Bitrix: Railway sync success for product XXXXX
Railway: 📨 Received webhook: product.updated for product XXXXX
```

---

### Test 3: Delete Product

**Steps:**
1. Delete the test product in Bitrix
2. Check logs

**Expected Behavior:**
- Product soft deleted (enabled=False in Railway)
- Visual search no longer returns this product

---

## 📊 Monitoring Commands

### Check Bitrix Logs
```bash
ssh root@185.125.90.141
tail -f /var/log/httpd/error_log | grep Railway
```

**Expected output when product created/updated:**
```
Railway sync success for product 123456
```

### Check Railway Logs
```bash
railway logs --service figma-product-catalog | grep webhook
```

**Expected output:**
```
📨 Received webhook: product.created for product 123456
✅ Created product 123456 with 3 images
```

### Check Visual Search Stats
```bash
curl https://visual-search.alekenov.workers.dev/stats
```

**Expected output:**
```json
{
  "total_indexed": 15,
  "last_indexed_at": "2025-10-20 22:30:00"
}
```

### Check Product in Railway Database
```bash
curl "https://figma-product-catalog-production.up.railway.app/api/v1/products/?shop_id=8&enabled_only=false" | \
  python3 -c "import sys, json; products = json.load(sys.stdin); print(f'Total products: {len(products)}')"
```

---

## 🔧 Troubleshooting

### Issue: Webhook not called
**Check:**
1. Bitrix logs for errors
   ```bash
   tail -100 /var/log/httpd/error_log | grep -i "railway\|error"
   ```

2. Verify init.php syntax
   ```bash
   php -l /home/bitrix/www/local/php_interface/init.php
   ```

3. Restart Apache if needed
   ```bash
   systemctl reload httpd
   ```

### Issue: Railway returns 401
**Cause:** Webhook secret mismatch

**Solution:**
```bash
# Verify Railway secret
railway variables --kv | grep WEBHOOK_SECRET

# Should output: cvety-webhook-2025-secure-key
```

### Issue: Visual Search not indexing
**Check Cloudflare Worker logs:**
- Go to Cloudflare Dashboard → Workers → visual-search → Logs
- Look for errors during reindex

**Common causes:**
- Image URL not accessible
- Image too large (>10MB)
- Network timeout

---

## ✅ Success Checklist

- [x] Railway Backend deployed
- [x] Visual Search Worker deployed
- [x] Bitrix event handler installed
- [x] Apache reloaded
- [x] Event handlers loaded (verified in logs)
- [x] Documentation committed to Git
- [ ] **Test product created in Bitrix** ← DO THIS NOW
- [ ] **Webhook called successfully** ← VERIFY AFTER TEST
- [ ] **Product indexed in Visual Search** ← VERIFY AFTER TEST

---

## 📁 Documentation Files

All documentation available in repository:

| File | Description |
|------|-------------|
| `INSTALLATION_COMPLETE.md` | This file - installation summary |
| `QUICK_START.md` | Quick start guide |
| `DEPLOYMENT_SUCCESS.md` | Full deployment report |
| `TESTING_RESULTS.md` | Automated testing results |
| `BITRIX_EVENT_HANDLER.md` | Bitrix handler documentation |
| `test-webhook-flow.sh` | Automated test script |

---

## 🎯 Next Steps

### 1. Create Test Product (5 minutes)
1. Go to Bitrix admin panel
2. Create product "TEST Visual Search Sync" with photo
3. Save and check logs

### 2. Verify Webhook Flow (2 minutes)
```bash
# Terminal 1: Bitrix logs
ssh root@185.125.90.141 'tail -f /var/log/httpd/error_log | grep Railway'

# Terminal 2: Railway logs
railway logs --service figma-product-catalog --follow | grep webhook
```

### 3. Test Visual Search (2 minutes)
```bash
# Upload test image
curl -X POST "https://visual-search.alekenov.workers.dev/search" \
  -F "image=@/path/to/bouquet.jpg"

# Should return similar products
```

---

## 🎉 System is Live!

After creating the test product, your system will be **fully automated**:

```
Manager creates product in Bitrix
    ↓
Bitrix triggers OnAfterIBlockElementAdd
    ↓
syncProductToRailway() sends webhook to Railway
    ↓
Railway creates Product + ProductImage in database
    ↓
Railway triggers background reindex task
    ↓
Visual Search Worker fetches product from Railway API
    ↓
Worker downloads image from cvety.kz
    ↓
Worker generates CLIP embedding
    ↓
Worker stores in Vectorize + D1
    ↓
Product is now searchable by image!
```

**Zero manual intervention required!**

---

## 📞 Support

**Issues:**
- Check logs first (Bitrix, Railway, Cloudflare)
- Review troubleshooting section above
- Verify all components are running

**Rollback:**
If needed, restore from backup:
```bash
ssh root@185.125.90.141
cp /home/bitrix/www/local/php_interface/init.php.backup-20251020-221707 \
   /home/bitrix/www/local/php_interface/init.php
systemctl reload httpd
```

---

**Installation Date:** 2025-10-20
**Installed By:** Claude Code + @alekenov
**Status:** ✅ Production Ready
**Waiting For:** Manual test in Bitrix admin panel

**Test the system now by creating a product in Bitrix!** 🚀
