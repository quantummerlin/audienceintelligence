# ============================================================
# PythonAnywhere WSGI entry point
#
# In the PythonAnywhere dashboard:
#   Web tab → WSGI configuration file → paste this path:
#   /home/YOURUSERNAME/audienceintelligence/downloader_api/wsgi.py
#
# Replace YOURUSERNAME with your PythonAnywhere username below.
# ============================================================

import sys
import os

# Add the API folder and the project root (for fb_video_downloader)
sys.path.insert(0, '/home/YOURUSERNAME/audienceintelligence/downloader_api')
sys.path.insert(0, '/home/YOURUSERNAME/audienceintelligence')

from app import app as application  # noqa: F401  (PythonAnywhere looks for 'application')
