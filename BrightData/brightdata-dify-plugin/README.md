# Bright Data Web Scraping Plugin
A web scraping API integration to enable web unlocking and data extraction capabilities on Dify.

### 1. Install in Dify
1. Click Install
2. Configure your API key

![image](https://github.com/user-attachments/assets/f03fdc7b-ae7e-446e-a4f3-12fb765e168d)

### 2. Setup Bright Data Account
1. Visit [Bright Data](https://brightdata.com/) and create an account
2. You will get your API key by email at the end of the signup process or you can navigate to your account settings to find it.
4. Insert your API key to Dify

### 3. Create Your First Workflow
1. Go to **Dify Studio** → **Workflow**
2. Add one of the **Bright Data Web Scraper** tools:
   - **Structured Data Feeds** - Extract structured data from 20+ platforms
   - **Scrape As Markdown** - Convert any webpage to clean markdown
   - **Search Engine** - Get search results from Google, Bing, Yandex

3. Enter your Bright Data API key when prompted
5. You can connect an **LLM node** to process and summarize the scraped data

## 💡 Example Workflow
(see workflow in banner image)
**Sample Use Case**: Extract Amazon product information and create a summary
1. **START** → Input: **Product** URL
2. **STRUCTURED DATA FEEDS** → Extract product details
3. **LLM** → Summarize into easy-to-read text
4. **END** → Output: Clean product summary
Important tips;
- Referance every stage of the workflow to the output of the previos stage
- Set a high charecter limit in input fields (for the URL input field choose the "short paragraph" var option)

## 📋 Available Tools

### 🔍 Structured Data Feeds
Extract structured data from popular platforms:
- **E-commerce**: Amazon, eBay, Walmart, Best Buy, Etsy, Zara
- **Social Media**: Instagram, Facebook, TikTok, YouTube, X (Twitter)
- **Professional**: LinkedIn profiles, companies, jobs
- **Business**: Crunchbase, ZoomInfo
- **Maps & Reviews**: Google Maps, booking sites
- **News**: Reuters and other news sources

### 📄 Scrape As Markdown
Convert any webpage into clean, readable markdown format perfect for:
- Content analysis
- Documentation extraction
- Article processing

### 🔎 Search Engine
Get search results from major search engines:
- Google
- Bing
- Yandex

## 🆘 Support
- **Issues**: [GitHub Issues](https://github.com/idanvilenski/BrightData_Dify_Plugin/issues)
- **Bright Data Support**: [Bright Data Help Center](https://help.brightdata.com/)
- **Dify Documentation**: [Dify Docs](https://docs.dify.ai/)

Thanks.