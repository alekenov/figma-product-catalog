#!/bin/bash
# Deploy script to add product images to shop_id=8 in production

set -e

echo "📦 Deploying image upload script to Railway..."

cd /Users/alekenov/figma-product-catalog/backend

# Create a one-time deployment script
railway run python3 add_images_to_shop8.py --service figma-product-catalog

echo "✅ Deployment complete!"
