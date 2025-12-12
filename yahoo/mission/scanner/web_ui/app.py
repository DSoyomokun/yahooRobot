"""
Simple web UI for viewing paper scans (Professor view).
Flask-based web interface to browse and view scanned papers.
"""
import os
import sys
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from yahoo.mission.scanner.storage import DB_PATH

app = Flask(__name__)

def get_all_scans():
    """Get all scans from database."""
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp, image_path, student_name, ocr_raw, 
               ocr_confidence, processed, weight_grams
        FROM paper_scans
        ORDER BY timestamp DESC
    """)
    
    scans = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return scans


def get_statistics():
    """Get database statistics."""
    if not os.path.exists(DB_PATH):
        return {}
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM paper_scans")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM paper_scans WHERE processed = 1")
    processed = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(DISTINCT student_name) FROM paper_scans WHERE student_name IS NOT NULL")
    unique_students = cur.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total,
        "processed": processed,
        "pending": total - processed,
        "unique_students": unique_students
    }


@app.route('/')
def index():
    """Main page - list all scans."""
    scans = get_all_scans()
    stats = get_statistics()
    return render_template('index.html', scans=scans, stats=stats)


@app.route('/api/scans')
def api_scans():
    """API endpoint to get all scans as JSON."""
    scans = get_all_scans()
    return jsonify(scans)


@app.route('/api/statistics')
def api_statistics():
    """API endpoint to get statistics."""
    return jsonify(get_statistics())


@app.route('/image/<int:scan_id>')
def get_image(scan_id):
    """Serve image file for a scan."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT image_path FROM paper_scans WHERE id = ?", (scan_id,))
    result = cur.fetchone()
    conn.close()
    
    if not result:
        return "Image not found", 404
    
    image_path = result[0]
    if not os.path.exists(image_path):
        return "Image file not found", 404
    
    return send_file(image_path, mimetype='image/png')


if __name__ == '__main__':
    print("🌐 Starting Paper Scanner Web UI...")
    print("   Open http://localhost:5000 in your browser")
    print("   Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)


