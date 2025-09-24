# 🔗 Social Media Link Preview Setup

This guide explains how to set up link preview images for RootSource AI when sharing on social media platforms.

## 📋 What's Included

### ✅ Meta Tags Added to `index.html`
- **Open Graph tags** for Facebook, LinkedIn, WhatsApp
- **Twitter Card tags** for Twitter/X
- **SEO meta tags** for better search engine visibility
- **Theme colors** and mobile app configurations

### 🎨 Social Preview Image
- **Generated image**: `assets/social-preview.png` (1200x630px)
- **Professional design** with RootSource AI branding
- **Dashboard mockup** showing the AI interface
- **Key features highlighted** with icons and text

## 🚀 How to Enable Link Previews

### 1. **GitHub Repository Social Preview**
1. Go to your repository: `https://github.com/Rafi-uzzaman/RootSource`
2. Click **Settings** tab
3. Scroll to **Social preview** section
4. Upload `assets/social-preview.png`
5. Save changes

### 2. **Website Link Previews**
The meta tags in `index.html` will automatically work when your site is deployed to:
- GitHub Pages
- Netlify
- Vercel
- Any web hosting platform

### 3. **Update URLs in Meta Tags**
When you deploy, update these URLs in `index.html`:
```html
<!-- Replace with your actual deployment URL -->
<meta property="og:url" content="https://your-username.github.io/RootSource/">
<meta property="og:image" content="https://your-username.github.io/RootSource/assets/social-preview.png">
<meta name="twitter:url" content="https://your-username.github.io/RootSource/">
<meta name="twitter:image" content="https://your-username.github.io/RootSource/assets/social-preview.png">
```

## 📱 Supported Platforms

### ✅ Platforms with Rich Link Previews
- **Facebook** - Shows large image with title and description
- **Twitter/X** - Large card format with image
- **LinkedIn** - Professional preview with company branding
- **WhatsApp** - Thumbnail with title and description
- **Telegram** - Rich media preview
- **Discord** - Embedded preview card
- **Slack** - Unfurled link with image

### 🎯 Preview Format
- **Image**: 1200x630 pixels (optimal for all platforms)
- **Title**: "🌱 RootSource AI - Revolutionizing Agriculture Through AI"
- **Description**: Highlights key features and benefits
- **Colors**: Agricultural green theme matching brand

## 🔧 Testing Link Previews

### Debug Tools:
- **Facebook**: [Sharing Debugger](https://developers.facebook.com/tools/debug/)
- **Twitter**: [Card Validator](https://cards-dev.twitter.com/validator)
- **LinkedIn**: [Post Inspector](https://www.linkedin.com/post-inspector/)
- **General**: [OpenGraph.xyz](https://www.opengraph.xyz/)

### Quick Test:
1. Deploy your site with updated meta tags
2. Share the URL on any social platform
3. The preview should show automatically

## 📊 Best Practices

### ✅ Do's
- Keep title under 60 characters
- Description under 155 characters
- Use high-quality images (1200x630px)
- Include relevant keywords
- Test on multiple platforms

### ❌ Don'ts
- Use copyrighted images
- Make text too small to read
- Forget to update URLs after deployment
- Use images smaller than 1200x630px

## 🎨 Regenerating the Social Preview

To create a new social preview image:

```bash
# Install dependencies
pip install Pillow

# Run the generator
python generate_social_preview.py
```

The script will create a new `assets/social-preview.png` with your latest branding and features.

---

**Result**: When someone shares your RootSource AI link, they'll see a professional preview showcasing your AI agricultural assistant! 🌱✨