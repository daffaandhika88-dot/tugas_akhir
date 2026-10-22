
"""
YouTube Music Playlist to MP3 Converter (Fixed Version)
Memaksa konversi ke MP3 dengan berbagai cara

Dependencies:
pip install yt-dlp

Pastikan FFmpeg sudah terinstall!
"""

import os
import re
import yt_dlp
import subprocess
import sys
from pathlib import Path

def check_ffmpeg():
    """Periksa apakah FFmpeg tersedia"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, check=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ffmpeg_instructions():
    """Tampilkan instruksi install FFmpeg"""
    print("\n" + "="*60)
    print("❌ FFMPEG TIDAK DITEMUKAN!")
    print("="*60)
    print("FFmpeg diperlukan untuk konversi ke MP3!")
    print("\n📥 CARA INSTALL FFMPEG:")
    
    if sys.platform.startswith('win'):
        print("\n🪟 WINDOWS:")
        print("1. Download dari: https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extract ke C:\\ffmpeg")
        print("3. Tambahkan C:\\ffmpeg\\bin ke PATH")
        print("4. Atau install via chocolatey: choco install ffmpeg")
        
    elif sys.platform.startswith('darwin'):
        print("\n🍎 macOS:")
        print("brew install ffmpeg")
        
    elif sys.platform.startswith('linux'):
        print("\n🐧 LINUX:")
        print("Ubuntu/Debian: sudo apt install ffmpeg")
        print("Fedora/CentOS: sudo yum install ffmpeg")
        print("Arch: sudo pacman -S ffmpeg")
    
    print("\n🔄 Setelah install, restart program ini!")
    print("="*60)

class YouTubeConverter:
    def __init__(self, output_dir="mp3_downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Konfigurasi yang memaksa konversi ke MP3
        self.ydl_opts = {
            # Format audio terbaik
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
            
            # Postprocessor untuk konversi MP3
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            
            # Template nama file (akan otomatis jadi .mp3)
            'outtmpl': str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
            
            # Pengaturan lain
            'ignoreerrors': True,
            'no_warnings': False,
            'writethumbnail': False,
            'writeinfojson': False,
            
            # PENTING: Hapus file asli setelah konversi
            'keepvideo': False,
        }

    def convert_single_file(self, input_file, output_file):
        """Konversi manual file ke MP3 jika yt-dlp gagal"""
        try:
            cmd = [
                'ffmpeg',
                '-i', str(input_file),
                '-codec:a', 'libmp3lame',
                '-b:a', '192k',
                '-y',  # Overwrite file yang sudah ada
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Hapus file asli setelah konversi berhasil
                input_file.unlink()
                print(f"✅ Berhasil konversi: {output_file.name}")
                return True
            else:
                print(f"❌ Gagal konversi: {input_file.name}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error konversi {input_file.name}: {e}")
            return False

    def cleanup_and_convert(self):
        """Bersihkan file non-MP3 dan konversi ke MP3"""
        non_mp3_files = []
        
        # Cari semua file audio non-MP3
        for ext in ['*.webm', '*.m4a', '*.ogg', '*.aac', '*.opus']:
            non_mp3_files.extend(self.output_dir.glob(ext))
        
        if non_mp3_files:
            print(f"\n🔄 Ditemukan {len(non_mp3_files)} file yang perlu dikonversi ke MP3...")
            
            for file in non_mp3_files:
                output_file = file.with_suffix('.mp3')
                print(f"Mengkonversi: {file.name} -> {output_file.name}")
                self.convert_single_file(file, output_file)

    def download_playlist(self, url):
        """Download playlist dan pastikan jadi MP3"""
        print(f"🎵 Download playlist: {url}")
        print(f"📁 Folder output: {self.output_dir.absolute()}")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info dulu
                print("📋 Menganalisis playlist...")
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    total = len([e for e in info['entries'] if e])
                    print(f"🎧 Ditemukan {total} lagu")
                    print(f"📝 Playlist: {info.get('title', 'Unknown')}")
                    
                    # Download
                    print("\n⬇️ Memulai download...\n")
                    ydl.download([url])
                    
                    # Konversi file yang belum MP3
                    self.cleanup_and_convert()
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        return False

    def download_single(self, url):
        """Download satu video"""
        print(f"🎵 Download video: {url}")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
                self.cleanup_and_convert()
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def list_files(self):
        """Tampilkan file MP3 yang berhasil didownload"""
        mp3_files = list(self.output_dir.glob("*.mp3"))
        
        if mp3_files:
            print(f"\n🎵 File MP3 berhasil didownload ({len(mp3_files)} file):")
            for i, file in enumerate(mp3_files, 1):
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"{i:2d}. {file.name} ({size_mb:.1f} MB)")
        else:
            print("\n❌ Tidak ada file MP3 ditemukan")
            
            # Cek apakah ada file lain
            other_files = []
            for ext in ['*.webm', '*.m4a', '*.ogg']:
                other_files.extend(self.output_dir.glob(ext))
            
            if other_files:
                print(f"\n⚠️ Ditemukan {len(other_files)} file dalam format lain:")
                for file in other_files:
                    print(f"   - {file.name}")
                print("\n💡 Jalankan opsi konversi manual atau pastikan FFmpeg terinstall")

def main():
    print("🎵 YouTube Music to MP3 Converter (Fixed Version)")
    print("="*55)
    
    # Cek FFmpeg
    if not check_ffmpeg():
        install_ffmpeg_instructions()
        return
    
    converter = YouTubeConverter()
    
    while True:
        print("\n📋 MENU:")
        print("1. ⬇️  Download Playlist ke MP3")
        print("2. ⬇️  Download 1 Lagu ke MP3")  
        print("3. 🔄 Konversi file existing ke MP3")
        print("4. 📂 Lihat file MP3")
        print("5. 🚪 Keluar")
        
        choice = input("\n👉 Pilih (1-5): ").strip()
        
        if choice == "1":
            url = input("\n🔗 URL Playlist YouTube Music: ").strip()
            if url and "list=" in url:
                if converter.download_playlist(url):
                    print("\n✅ Playlist berhasil didownload!")
                    converter.list_files()
                else:
                    print("\n❌ Gagal download playlist")
            else:
                print("❌ URL playlist tidak valid!")
                
        elif choice == "2":
            url = input("\n🔗 URL Video YouTube: ").strip()
            if url:
                if converter.download_single(url):
                    print("\n✅ Video berhasil didownload!")
                    converter.list_files()
                else:
                    print("\n❌ Gagal download video")
            else:
                print("❌ URL tidak boleh kosong!")
                
        elif choice == "3":
            print("\n🔄 Mengkonversi file existing ke MP3...")
            converter.cleanup_and_convert()
            converter.list_files()
            
        elif choice == "4":
            converter.list_files()
            
        elif choice == "5":
            print("\n👋 Terima kasih!")
            break
            
        else:
            print("❌ Pilihan tidak valid!")

if __name__ == "__main__":
    main()