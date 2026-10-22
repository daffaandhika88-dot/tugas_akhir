"""
YouTube Playlist to MP3 Downloader
Mengunduh playlist YouTube Music dan menyimpannya sebagai file MP3

Requirements:
pip install yt-dlp

Note: yt-dlp adalah fork yang lebih baik dari youtube-dl
"""

import os
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp belum terinstall!")
    print("Jalankan: pip install yt-dlp")
    sys.exit(1)


class YouTubePlaylistDownloader:
    def __init__(self, output_folder="YouTube_Music"):
        """
        Inisialisasi downloader
        
        Args:
            output_folder: Nama folder untuk menyimpan file MP3
        """
        self.output_folder = output_folder
        self.create_output_folder()
    
    def create_output_folder(self):
        """Membuat folder output jika belum ada"""
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        print(f"✓ Folder output: {os.path.abspath(self.output_folder)}")
    
    def download_playlist(self, playlist_url, audio_quality='192'):
        """
        Download playlist dari YouTube
        
        Args:
            playlist_url: URL playlist YouTube
            audio_quality: Kualitas audio (128, 192, 256, 320 kbps)
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }],
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'ignoreerrors': True,  # Skip video yang error
            'no_warnings': False,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            print(f"\n{'='*60}")
            print(f"Memulai download playlist...")
            print(f"URL: {playlist_url}")
            print(f"Kualitas audio: {audio_quality} kbps")
            print(f"{'='*60}\n")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info playlist
                print("Mengambil informasi playlist...")
                info = ydl.extract_info(playlist_url, download=False)
                
                if 'entries' in info:
                    total_videos = len([e for e in info['entries'] if e])
                    print(f"\n✓ Ditemukan {total_videos} video dalam playlist")
                    print(f"✓ Playlist: {info.get('title', 'Unknown')}\n")
                    
                    # Download
                    ydl.download([playlist_url])
                    
                    print(f"\n{'='*60}")
                    print(f"✓ SELESAI! Semua file MP3 tersimpan di: {os.path.abspath(self.output_folder)}")
                    print(f"{'='*60}")
                else:
                    # Single video
                    print("Ini adalah single video, bukan playlist")
                    ydl.download([playlist_url])
                    print(f"\n✓ Download selesai!")
                    
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            print("\nPastikan:")
            print("1. URL playlist valid")
            print("2. Koneksi internet stabil")
            print("3. FFmpeg terinstall (untuk konversi ke MP3)")
    
    def progress_hook(self, d):
        """Hook untuk menampilkan progress download"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\rDownloading: {percent} | Speed: {speed} | ETA: {eta}", end='')
        elif d['status'] == 'finished':
            print(f"\n✓ Download selesai, converting ke MP3...")


def main():
    """Fungsi utama"""
    print("="*60)
    print("YouTube Playlist to MP3 Downloader")
    print("="*60)
    
    # Input dari user
    playlist_url = input("\nMasukkan URL playlist YouTube: ").strip()
    
    if not playlist_url:
        print("✗ URL tidak boleh kosong!")
        return
    
    # Pilihan kualitas audio
    print("\nPilih kualitas audio:")
    print("1. 128 kbps (ukuran kecil)")
    print("2. 192 kbps (recommended)")
    print("3. 256 kbps (kualitas tinggi)")
    print("4. 320 kbps (kualitas maksimal)")
    
    quality_map = {'1': '128', '2': '192', '3': '256', '4': '320'}
    choice = input("\nPilihan (1-4) [default: 2]: ").strip() or '2'
    audio_quality = quality_map.get(choice, '192')
    
    # Nama folder output
    folder_name = input("\nNama folder output [default: YouTube_Music]: ").strip() or "YouTube_Music"
    
    # Download
    downloader = YouTubePlaylistDownloader(output_folder=folder_name)
    downloader.download_playlist(playlist_url, audio_quality)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Download dibatalkan oleh user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error tidak terduga: {str(e)}")
        sys.exit(1)