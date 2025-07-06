# FAVICON SETUP INSTRUCTIONS

## 🎯 How to Add Your Logo as Favicon

### Step 1: Prepare Your Logo
1. **Get your logo file** (PNG, JPG, or SVG format)
2. **Ensure high quality** - at least 512x512 pixels for best results
3. **Use square format** - logos work best when they're square

### Step 2: Generate Favicon Files
Use any of these free online tools to convert your logo:

#### Recommended Tools:
- **favicon.io** (https://favicon.io/favicon-converter/)
- **realfavicongenerator.net** (https://realfavicongenerator.net/)
- **convertio.co** (https://convertio.co/png-ico/)

#### Required Sizes:
- `favicon.ico` (16x16, 32x32, 48x48)
- `favicon-16x16.png`
- `favicon-32x32.png`
- `apple-touch-icon.png` (180x180)
- `android-chrome-192x192.png`
- `android-chrome-512x512.png`

### Step 3: Replace Files
Upload your generated files to the `/static/` directory, replacing:
- `/static/favicon.ico`
- `/static/favicon.svg`
- `/static/favicon-16x16.png`
- `/static/favicon-32x32.png`
- `/static/apple-touch-icon.png`
- `/static/android-chrome-192x192.png`
- `/static/android-chrome-512x512.png`

### Step 4: Verify
After uploading, your favicon will appear in:
- ✅ Browser tabs
- ✅ Bookmarks
- ✅ Mobile home screen icons
- ✅ Web app manifest

## 📁 Current File Structure
```
/static/
├── favicon.ico          (Replace with your logo)
├── favicon.svg          (Replace with your logo)
├── favicon-16x16.png    (Create from your logo)
├── favicon-32x32.png    (Create from your logo)
├── apple-touch-icon.png (Create from your logo)
├── android-chrome-192x192.png (Create from your logo)
├── android-chrome-512x512.png (Create from your logo)
└── site.webmanifest    (Already configured)
```

## 🎨 Templates Updated
All your HTML templates now include proper favicon links:
- ✅ `index.html` - Main page
- ✅ `onboarding.html` - User registration
- ✅ `secure_pin_verification.html` - PIN entry
- ✅ `pin-entry.html` - Alternative PIN page

## 🔧 Quick Test
After uploading your favicon files:
1. Clear browser cache (Ctrl+F5)
2. Visit your website
3. Check browser tab for your logo
4. Add to mobile home screen to test app icon

## 💡 Pro Tips
- **Keep it simple** - Complex logos may not be visible at small sizes
- **High contrast** - Ensure visibility on both light and dark backgrounds
- **Test on mobile** - Check how it looks as a home screen icon
- **Use brand colors** - Maintain brand consistency

Your favicon system is now ready for your logo! 🎉
