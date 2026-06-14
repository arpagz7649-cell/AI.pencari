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
                    "data": jawaban_interaktif, # Data interaktif disuntikkan di sini
                    "url": url_sumber,
                    "waktu_proses": round(time.time() - start_time, 4)
                }
                
                # Simpan hasil eksekusi ke cache
                self.save_to_cache(query, payload)
                return payload
