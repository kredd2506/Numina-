# GitHub Pages Deployment Guide

This guide will help you deploy the Numina website to GitHub Pages.

## Prerequisites

- A GitHub account
- Git installed on your local machine
- The Numina repository cloned locally

---

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure all files are committed:

```bash
git add .
git commit -m "Add GitHub Pages website with architecture diagram"
git push origin main
```

### 2. Enable GitHub Pages

1. Navigate to your repository on GitHub
2. Click on **Settings** (top right)
3. Scroll down to **Pages** in the left sidebar (under "Code and automation")
4. Under **Source**, configure:
   - **Branch:** `main`
   - **Folder:** `/docs`
5. Click **Save**

### 3. Wait for Deployment

- GitHub will automatically build and deploy your site
- This usually takes 1-2 minutes
- You'll see a green checkmark when it's ready

### 4. Access Your Live Website

Your website will be available at:

```
https://[your-github-username].github.io/[repository-name]/
```

For example:
- Username: `johndoe`
- Repository: `numina`
- URL: `https://johndoe.github.io/numina/`

### 5. Update Links in the Website

Edit the following files to replace placeholder links:

**In `docs/index.html`:**

Replace all instances of:
- `yourusername` → your actual GitHub username
- `numina` → your repository name (if different)

Search for these sections:
1. Navigation GitHub button (line ~119)
2. Footer GitHub link (line ~430+)
3. CTA section GitHub link (line ~390+)

**Example:**

Change:
```html
<a href="https://github.com/yourusername/numina" target="_blank">
```

To:
```html
<a href="https://github.com/johndoe/numina" target="_blank">
```

### 6. Verify Deployment

1. Visit your GitHub Pages URL
2. Check that:
   - All sections load correctly
   - Navigation links work
   - Architecture diagram is visible
   - External links point to the correct locations

---

## Custom Domain (Optional)

If you want to use a custom domain like `numina.ai`:

### 1. Create CNAME File

Create a file named `CNAME` in the `docs/` folder:

```bash
echo "numina.ai" > docs/CNAME
```

### 2. Configure DNS

Add these DNS records with your domain provider:

**For root domain (numina.ai):**
```
Type: A
Name: @
Value: 185.199.108.153
```

Add three more A records with these IPs:
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

**For www subdomain (www.numina.ai):**
```
Type: CNAME
Name: www
Value: [your-username].github.io
```

### 3. Enable HTTPS

1. Go to GitHub repository Settings → Pages
2. Check **Enforce HTTPS**
3. Wait for SSL certificate to be provisioned (can take up to 24 hours)

---

## Troubleshooting

### Site Not Loading

**Issue:** 404 error or blank page

**Solution:**
- Ensure you selected `/docs` folder (not root `/`)
- Check that `index.html` exists in the `docs/` folder
- Wait 2-3 minutes after enabling Pages

### Architecture Diagram Not Showing

**Issue:** Broken image icon or missing diagram

**Solution:**
- Verify `Architecture Diagram.png` is in the root folder
- Check the image path in `index.html`:
  ```html
  <img src="../Architecture Diagram.png" alt="Numina System Architecture">
  ```
- Ensure the file is committed and pushed to GitHub

### CSS/Styles Not Loading

**Issue:** Unstyled HTML page

**Solution:**
- Verify `styles.css` and `script.js` are in the `docs/` folder
- Check browser console (F12) for errors
- Clear browser cache and hard refresh (Ctrl+Shift+R)

### Custom Domain Not Working

**Issue:** Domain shows error or doesn't load

**Solution:**
- Verify DNS records are correct
- Wait 24-48 hours for DNS propagation
- Check CNAME file contains only your domain (no protocol)
- Ensure HTTPS enforcement is checked in GitHub settings

---

## Updating the Website

To make changes to your live website:

1. Edit files in the `docs/` folder locally
2. Commit and push changes:
   ```bash
   git add docs/
   git commit -m "Update website content"
   git push origin main
   ```
3. GitHub Pages will automatically rebuild (1-2 minutes)

---

## File Structure

```
docs/
├── index.html          # Main website HTML
├── styles.css          # All styles and responsive design
├── script.js           # Interactive features and animations
├── _config.yml         # Jekyll configuration (optional)
└── DEPLOYMENT.md       # This file
```

---

## Performance Tips

1. **Image Optimization:**
   - Compress `Architecture Diagram.png` using tools like TinyPNG
   - Consider converting to WebP format for faster loading

2. **Caching:**
   - GitHub Pages automatically caches static assets
   - Use versioned filenames for cache busting if needed

3. **Analytics:**
   - Add Google Analytics by inserting tracking code in `index.html`
   - Track visitor metrics and behavior

---

## Support

For issues with:
- **GitHub Pages**: [GitHub Pages Documentation](https://docs.github.com/en/pages)
- **Custom Domains**: [Configuring a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- **SSL/HTTPS**: [Securing your site with HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)

---

**Happy Deploying! 🚀**
