# 📄 PDF Image Extractor

A Django web application that allows users to upload PDF files, automatically extract embedded images, select specific ones, and download them bundled in a ZIP archive.

## 🚀 Features

- 📤 Upload PDF files
- 🖼️ Automatically extract all embedded images
- ✅ Select individual images
- 📦 Download selected images as a single ZIP file
- 🔐 User authentication and session-based access
- 📊 Track number of downloads per user

## 🛠️ Tech Stack

- **Backend**: Django
- **PDF Image Extraction**: PyMuPDF (fitz)
- **Frontend**: HTML, CSS, Tailwind CSS
- **Database**: SQLite (for development)
- **Authentication**: Django's built-in auth system

## ⚙️ Local Setup Instructions

1. **Create and activate a virtual environment:**

```bash
python -m venv env
# On Linux/macOS:
source env/bin/activate
# On Windows:
env\Scripts\activate
