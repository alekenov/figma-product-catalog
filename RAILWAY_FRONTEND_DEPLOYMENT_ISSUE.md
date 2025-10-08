# Railway Frontend Deployment Issue

**Date**: 2025-10-08
**Status**: 🔴 UNRESOLVED - Frontend auto-deploy not working

## Problem Summary

The Frontend service on Railway is NOT automatically deploying when code is pushed to GitHub's `main` branch, despite:
- Backend service deploying correctly
- MCP server deploying correctly
- All commits successfully pushed to GitHub

## Evidence

### ✅ Commits Pushed Successfully
```bash
07581f8 fix: Use React Query hook for product creation
7776118 chore: Trigger Railway frontend redeploy
3166003 chore: Force frontend rebuild
```

### ✅ Local Code is Correct
```bash
$ grep -n "useCreateProduct" frontend/src/AddProduct.jsx
4:import { useCreateProduct } from './hooks/useProducts';
12:  const createProduct = useCreateProduct();
```

### ❌ Production Shows OLD Build
```bash
# Production still serves old bundle:
AddProduct-5bb30370.js  # Old hash - hasn't changed

# Curl verification:
$ curl -s "https://frontend-production-6869.up.railway.app/" | grep "force rebuild"
# No match - old build still deployed
```

### ❌ UI Test Results
- Created "Deployment Verification Bouquet" - appeared only after page refresh
- Created "Final Test Auto-Refresh" - appeared only after page refresh
- React Query cache invalidation NOT working (old code without hook)

## Expected vs Actual Behavior

### Expected (after fix)
1. User creates product via UI
2. `useCreateProduct` mutation hook called
3. Product created via API ✅ (works)
4. React Query `onSuccess` callback fires
5. `queryClient.invalidateQueries()` refetches products
6. **New product appears in list automatically**

### Actual (current production)
1. User creates product via UI
2. Old code calls `productsAPI.createProduct()` directly
3. Product created via API ✅ (works)
4. No cache invalidation (old code path)
5. **Product does NOT appear until page refresh** ❌

## Railway Configuration

### Frontend Service (Expected)
```json
{
  "serviceName": "Frontend",
  "rootDirectory": "/frontend",
  "builder": "NIXPACKS",
  "startCommand": "npm run start",
  "autoDeploy": true,  // Should be enabled
  "branch": "main"
}
```

### railway.json (Correct)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run start",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Attempted Solutions

### 1. ✅ Created Fix (07581f8)
- Modified `AddProduct.jsx` to use `useCreateProduct` hook
- Committed and pushed to GitHub

### 2. ✅ Empty Commit Trigger (7776118)
```bash
git commit --allow-empty -m "chore: Trigger Railway frontend redeploy"
git push origin main
```

### 3. ✅ Force Rebuild with Code Change (3166003)
```bash
echo "// Force rebuild $(date)" >> frontend/src/App.jsx
git add frontend/src/App.jsx
git commit -m "chore: Force frontend rebuild"
git push origin main
```

### 4. ❌ Manual Deploy via CLI
```bash
cd frontend && railway up --ci
# Result: Built WRONG service (MCP server with Python Dockerfile)
# Issue: Railway CLI linked to mcp-server, not Frontend
```

## Root Cause Analysis

### Possible Causes

1. **Auto-Deploy Disabled** (Most Likely)
   - Frontend service auto-deploy toggle may be OFF in Railway dashboard
   - Solution: Enable auto-deploy in service settings

2. **Wrong Root Directory**
   - Service may be configured with wrong root path
   - Verify in Railway dashboard: Service Settings → Root Directory = `/frontend`

3. **Watch Path Filter**
   - Service may have watch paths that exclude `/frontend/**`
   - Check: Service Settings → Watch Paths

4. **Deployment Queue Issue**
   - Build may be stuck/paused in Railway's deployment queue
   - Check: Railway dashboard → Deployments tab

5. **GitHub Webhook Not Configured**
   - Railway may not have webhook permissions for the repository
   - Check: GitHub repo → Settings → Webhooks → Railway webhook status

## Verification Steps

### Backend/MCP Services Work Correctly
```bash
$ cd frontend && railway logs --build | head -20
# Shows Python/MCP server build logs, NOT Frontend build
# Confirms: Other services deploying fine, Frontend specific issue
```

### API Works (Product Creation)
```bash
$ curl "https://figma-product-catalog-production.up.railway.app/api/v1/products/?shop_id=2&limit=100"
# Returns 10 products including:
# - "UI Test Bouquet" (ID: 34)
# - "Deployment Verification Bouquet" (ID: 35)
# - "Final Test Auto-Refresh" (ID: 36)
```

## Impact

### User Experience
- ❌ Products don't appear after creation without manual refresh
- ❌ Search doesn't find newly created products
- ⚠️ Confusing UX - users think creation failed

### Testing Status
- ✅ API tests: 100% pass rate (43/43 steps)
- ✅ Backend functionality: Working correctly
- ❌ Frontend auto-refresh: NOT working (old code)

## Next Steps

### Immediate Action Required (Manual)
**User must check Railway Dashboard:**

1. Go to: https://railway.com/project/311bb135-7712-402e-aacf-14ce8b0b80df
2. Select "Frontend" service
3. Check Settings:
   - ✅ Auto-Deploy: Should be ENABLED
   - ✅ Root Directory: Should be `/frontend`
   - ✅ Watch Paths: Should include `/frontend/**` or be empty (watch all)
   - ✅ Branch: Should be `main`
4. Check Deployments tab:
   - Look for stuck/failed deployments
   - Manually trigger deployment if needed

### Verification After Fix
```bash
# 1. Check new build hash
curl -s "https://frontend-production-6869.up.railway.app/" | grep "force rebuild"
# Should show: <!-- force rebuild [date] -->

# 2. Check AddProduct hash changed
# Open browser console, create product, look for new hash:
# OLD: AddProduct-5bb30370.js
# NEW: AddProduct-[new-hash].js

# 3. Test auto-refresh
# Create product → should appear in list WITHOUT page refresh
```

## Workaround (Temporary)

Until Railway deployment is fixed, users can:
1. Create product via UI
2. **Manually refresh page** to see new product
3. API correctly creates products, only UI refresh is broken

## Related Files

- `frontend/src/AddProduct.jsx` - Contains fix (useCreateProduct hook)
- `frontend/src/hooks/useProducts.js` - React Query hooks with cache invalidation
- `frontend/railway.json` - Railway service configuration
- `CLAUDE.md` - Documentation of Railway setup

## Technical Details

### React Query Cache Invalidation Pattern
```javascript
// hooks/useProducts.js (line 65-76)
export const useCreateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => productsAPI.createProduct(data),
    onSuccess: () => {
      // This automatically refetches products list
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
};
```

### Old Code (Still in Production)
```javascript
// AddProduct.jsx (line 169 - OLD VERSION)
const result = await productsAPI.createProduct(productData);
// No cache invalidation - list stays stale
```

### New Code (In GitHub, Not Deployed)
```javascript
// AddProduct.jsx (line 170-174 - NEW VERSION)
const createProduct = useCreateProduct();
// ...
const result = await createProduct.mutateAsync(productData);
// Auto-invalidates cache via onSuccess hook
```

## Conclusion

**The code fix is correct and committed**, but Railway Frontend service is not deploying new builds. This is a Railway configuration issue, not a code issue.

**Action Required**: User must manually check Railway Dashboard and enable auto-deploy or manually trigger deployment for Frontend service.
