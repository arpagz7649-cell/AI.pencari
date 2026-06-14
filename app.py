"""
SISTEM UTAMA ENGINE AI WIKIPEDIA
Arsitektur: Flask Enterprise Modular
Status: Clone Berhasil Diperbarui
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, session
import wikipediaapi

# ==========================================
# INSIALISASI SUBSISTEM LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] AI_LOG: %(message)s'
)
logger = logging.getLogger("AI_Wikipedia_Engine")

class AIWikipediaEngine:
    """Core engine untuk ekstrasi data, sanitasi, dan manajemen memori cache."""
    
    def __init__(self, language: str = 'id', user_agent: str = '') -> None:
        if not user_agent:
            raise ValueError("Kritikal: User-Agent tidak boleh kosong.")
            
        self.language = language
        self.user_agent = user_agent
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_summary_length = 1500
        
        try:
            self.wiki_agent = wikipediaapi.Wikipedia(
                language=self.language,
                user_agent=self.user_agent
            )
            logger.info("Koneksi API Wikipedia berhasil disinkronisasikan.")
        except Exception as error:
            logger.critical(f"Gagal menginisialisasi API: {str(error)}")
            raise error

    def sanitize_query(self, query: Optional[str]) -> str:
        """Saring input pengguna dari karakter ilegal dan spasi berlebih."""
        return query.strip() if query else ""

    def execute_search(self, raw_query: str) -> Dict[str, Any]:
        """Alur pemrosesan data utama."""
        start_time = time.time()
        query = self.sanitize_query(raw_query)
        
        if not query:
            return {
                "status": "error",
                "pesan": "Kueri pencarian kosong. Masukkan kata kunci valid.",
                "data": "",
                "waktu_proses": 0.0
            }
            
        # Periksa memori cache internal
        query_key = query.lower()
        if query_key in self.cache:
            logger.info(f"Mengambil data dari cache untuk: '{query}'")
            self.cache[query_key]["waktu_proses"] = round(time.time() - start_time, 4)
            return self.cache[query_key]

        try:
            logger.info(f"Mengirim permintaan data untuk topik: '{query}'")
            halaman = self.wiki_agent.page(query)
            
            if halaman.exists():
                # Ekstraksi komponen data secara mendalam
                ringkasan = halaman.summary[:self.max_summary_length]
                judul_resmi = halaman.title
                url_sumber = halaman.fullurl
                
                # Penggabungan hasil ekstraksi dengan protokol interaksi AI otomatis
                jawaban_interaktif = (
                    f"{ringkasan}\n\n"
                    f"🤖 [Sistem AI]: Proses ekstraksi data '{judul_resmi}' telah selesai. "
                    f"Apakah ada hal lain yang mau ditanyakan atau ingin Anda jelajahi lebih lanjut?"
                )
                
                payload = {
                    "status": "success",
                    "pesan": "Data berhasil diekstrak.",
                    "judul": judul_resmi,
                    "data": jawaban_interaktif,
                    "url": url_sumber,
                    "waktu_proses": round(time.time() - start_time, 4)
                }
                
                # Simpan hasil eksekusi ke cache
                self.cache[query_key] = payload
                return payload
            else:
                logger.warning(f"Topik '{query}' tidak ditemukan.")
                return {
                    "status": "not_found",
                    "pesan": f"Asisten AI tidak dapat menemukan informasi mengenai '{query}' di pangkalan data Wikipedia.",
                    "data": "",
                    "waktu_proses": round(time.time() - start_time, 4)
                }
                
        except Exception as system_error:
            logger.error(f"Kerusakan sistem pencarian: {str(system_error)}")
            return {
                "status": "fatal_error",
                "pesan": f"Terjadi kesalahan internal pada sistem AI: {str(system_error)}",
                "data": "",
                "waktu_proses": round(time.time() - start_time, 4)
            }

# ==========================================
# KONFIGURASI APLIKASI WEB FLASK
# ==========================================
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inisialisasi engine utama
ai_engine = AIWikipediaEngine(
    language='id',
    user_agent='AI_Wikipedia_Bot/2.0 (aswss@game.com)'
)

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    """Rute utama pengontrol lalu lintas data web."""
    jawaban_ai = ""
    meta_data: Dict[str, Any] = {}
    
    if 'history' not in session:
        session['history'] = []
        
    if request.method == 'POST':
        query_user = request.form.get('query', '')
        hasil_eksekusi = ai_engine.execute_search(query_user)
        
        if hasil_eksekusi["status"] == "success":
            jawaban_ai = hasil_eksekusi["data"]
            meta_data = {
                "judul": hasil_eksekusi["judul"],
                "url": hasil_eksekusi["url"],
                "waktu": hasil_eksekusi["waktu_proses"],
                "sukses": True
            }
            # Catat ke riwayat sesi
            local_history = session['history']
            if query_user.strip() not in local_history:
                local_history.append(query_user.strip())
                session['history'] = local_history[-5:]
        else:
            jawaban_ai = hasil_eksekusi["pesan"]
            meta_data = {
                "judul": "Gagal Mengekstrak",
                "url": "#",
                "waktu": hasil_eksekusi["waktu_proses"],
                "sukses": False
            }
            
    return render_template(
        'index.html', 
        jawaban=jawaban_ai, 
        meta=meta_data,
        riwayat=session['history']
    )

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Rute destruksi riwayat pencarian."""
    session.pop('history', None)
    from flask import redirect, url_for
    return redirect(url_for('index'))

# ==========================================
# RUNNER CORE SISTEM
# ==========================================
if __name__ == '__main__':
    logger.info("Mengaktifkan server lokal pada port 5000...")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
