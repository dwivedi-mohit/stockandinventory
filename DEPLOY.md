# 🚀 Deploy to Streamlit Cloud (FREE)

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Repository
Your code is already ready! The file `app_streamlit.py` contains the web GUI.

### Step 2: Create Streamlit Cloud Account
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign up with GitHub (recommended)
3. Click "New app"

### Step 3: Deploy
1. Select your repository: `dwivedi-mohit/stockandinventory`
2. Select branch: `main`
3. Select file: `app_streamlit.py`
4. Click "Deploy!"

### Step 4: Share Your Link
After deployment, you'll get a URL like:
```
https://stockandinventory-your-username.streamlit.app/
```

**That's it!** Your app is now live! 🎉

---

## ⚠️ Important: Database Configuration for Deployment

### For Local Testing (MySQL):
```bash
streamlit run app_streamlit.py
```

### For Production (Cloud):
You need to configure database credentials safely:

1. **Create `.env` file locally (don't commit this)**
   ```
   DB_HOST=your-mysql-host
   DB_USER=root
   DB_PASSWORD=your-password
   DB_NAME=inventory_db
   ```

2. **Update `app_streamlit.py` to use environment variables**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   DB_HOST = os.getenv("DB_HOST", "localhost")
   DB_USER = os.getenv("DB_USER", "root")
   DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
   DB_NAME = os.getenv("DB_NAME", "inventory_db")
   ```

3. **Set Secrets in Streamlit Cloud**
   - In your Streamlit Cloud app settings
   - Go to "Secrets" section
   - Add your database credentials:
     ```
     DB_HOST = "your-mysql-host"
     DB_USER = "root"
     DB_PASSWORD = "your-password"
     DB_NAME = "inventory_db"
     ```

---

## Alternative Deployment Options

### Option A: Railway.app (Recommended for databases)
1. Go to [railway.app](https://railway.app)
2. Create project
3. Add MySQL database
4. Deploy from GitHub
5. Set environment variables
6. Get public URL

### Option B: Render.com
1. Go to [render.com](https://render.com)
2. Create new web service
3. Connect GitHub
4. Deploy `app_streamlit.py`
5. Get live URL

### Option C: Heroku (Paid alternative)
1. Go to [heroku.com](https://heroku.com)
2. Create app
3. Connect to GitHub
4. Deploy

---

## Features in Web Version

✅ Dashboard with metrics
✅ Add products with form validation
✅ View all products in a table
✅ Add suppliers
✅ Purchase products
✅ Sell products
✅ Low stock alerts
✅ Sales & inventory reports
✅ Interactive charts

---

## Running Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app_streamlit.py

# Access at: http://localhost:8501
```

---

## Tips for Production

1. **Database Security**: Use environment variables for credentials
2. **Performance**: Enable caching with `@st.cache_resource`
3. **Scalability**: Consider managed databases (AWS RDS, Google Cloud SQL)
4. **Monitoring**: Check Streamlit Cloud logs if app fails
5. **Updates**: Push to GitHub to auto-deploy changes

---

## Support

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud/get-started)
- Issues? Check your database connection and environment variables

---

**Your live app will be available 24/7!** 🌐
