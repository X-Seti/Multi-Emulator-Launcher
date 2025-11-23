#!/usr/bin/env python3
#this belongs in apps/methods/igdb_downloader.py - Version: 2
# X-Seti - November23 2025 - Multi-Emulator Launcher - IGDB Artwork Downloader

"""
IGDB Artwork Downloader
Downloads game covers, screenshots, and metadata from IGDB API
Uses embedded credentials with basic obfuscation for convenience

SECURITY NOTE: This includes a shared API key for ease of use.
For production, consider: user registration, proxy server, or credential encryption.
"""

import requests
import json
import base64
from pathlib import Path
from typing import Optional, Dict, List
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QListWidget, QListWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

##Methods list -
# __init__
# download_artwork
# search_game
# _decode_credentials
# _download_image
# _get_igdb_token
# _save_artwork

##class IGDBDownloader -

class IGDBDownloader: #vers 2
    """Downloads artwork from IGDB API with embedded credentials"""
    
    # IGDB API endpoints
    TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    IGDB_API_URL = "https://api.igdb.com/v4"
    
    # Embedded credentials (base64 obfuscated)
    # TODO: Replace these with YOUR credentials after registering
    # To encode: base64.b64encode(b"your_id").decode()
    _EMBEDDED_ID = "eW91cl9jbGllbnRfaWRfaGVyZQ=="  # Replace with your encoded Client ID
    _EMBEDDED_SECRET = "eW91cl9jbGllbnRfc2VjcmV0X2hlcmU="  # Replace with your encoded Client Secret
    
    def __init__(self, artwork_dir: Path): #vers 2
        """Initialize IGDB downloader with embedded or user credentials
        
        Args:
            artwork_dir: Directory to save artwork
        """
        self.artwork_dir = Path(artwork_dir)
        self.artwork_dir.mkdir(parents=True, exist_ok=True)
        
        # Try embedded credentials first
        self.client_id, self.client_secret = self._decode_credentials()
        
        # Try to load user override from config (if they want their own key)
        self._load_user_credentials()
        
        self.access_token = None
    
    def _decode_credentials(self) -> tuple: #vers 1
        """Decode embedded credentials
        
        Returns:
            (client_id, client_secret) tuple
        """
        try:
            client_id = base64.b64decode(self._EMBEDDED_ID).decode()
            client_secret = base64.b64decode(self._EMBEDDED_SECRET).decode()
            
            # Check if they're still placeholder values
            if "your_client_id_here" in client_id or "your_client_secret_here" in client_secret:
                return None, None
            
            return client_id, client_secret
        except Exception as e:
            print(f"Error decoding credentials: {e}")
            return None, None
    
    def _load_user_credentials(self): #vers 1
        """Load user-provided API credentials from config (optional override)"""
        config_file = Path.cwd() / "config" / "igdb_credentials.json"
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    creds = json.load(f)
                    user_id = creds.get("client_id")
                    user_secret = creds.get("client_secret")
                    
                    # Override embedded credentials if user provided their own
                    if user_id and user_secret:
                        self.client_id = user_id
                        self.client_secret = user_secret
                        print("Using user-provided IGDB credentials")
            except Exception as e:
                print(f"Error loading user credentials: {e}")
    
    def _get_igdb_token(self) -> bool: #vers 1
        """Get OAuth token from Twitch"""
        if not self.client_id or not self.client_secret:
            print("IGDB credentials not configured")
            return False
        
        try:
            response = requests.post(
                self.TWITCH_TOKEN_URL,
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                return True
            else:
                print(f"Failed to get IGDB token: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error getting IGDB token: {e}")
            return False
    
    def search_game(self, game_name: str, platform: str = None) -> List[Dict]: #vers 1
        """Search for game on IGDB
        
        Args:
            game_name: Name of the game
            platform: Platform name (optional, helps narrow results)
            
        Returns:
            List of game results with metadata
        """
        if not self.access_token:
            if not self._get_igdb_token():
                return []
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        # Build query
        query = f'search "{game_name}"; fields name,cover.url,screenshots.url,summary,first_release_date; limit 10;'
        
        try:
            response = requests.post(
                f"{self.IGDB_API_URL}/games",
                headers=headers,
                data=query,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"IGDB search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching IGDB: {e}")
            return []
    
    def download_artwork(self, game_name: str, platform: str, game_id: int = None) -> bool: #vers 1
        """Download artwork for a game
        
        Args:
            game_name: Name of the game
            platform: Platform name
            game_id: IGDB game ID (if known)
            
        Returns:
            True if artwork downloaded successfully
        """
        # Search for game if ID not provided
        if not game_id:
            results = self.search_game(game_name, platform)
            if not results:
                print(f"No results found for: {game_name}")
                return False
            
            # Use first result
            game_data = results[0]
            game_id = game_data.get("id")
        else:
            # Fetch game data by ID
            if not self.access_token:
                if not self._get_igdb_token():
                    return False
            
            headers = {
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {self.access_token}"
            }
            
            query = f'where id = {game_id}; fields name,cover.url,screenshots.url;'
            
            try:
                response = requests.post(
                    f"{self.IGDB_API_URL}/games",
                    headers=headers,
                    data=query,
                    timeout=10
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        game_data = results[0]
                    else:
                        return False
                else:
                    return False
                    
            except Exception as e:
                print(f"Error fetching game data: {e}")
                return False
        
        # Download cover art (thumbnail)
        cover_url = game_data.get("cover", {}).get("url")
        if cover_url:
            # Convert to high-res URL
            cover_url = cover_url.replace("t_thumb", "t_cover_big")
            if not cover_url.startswith("http"):
                cover_url = "https:" + cover_url
            
            # Save as thumbnail
            thumbnail_dir = self.artwork_dir / platform / "thumbnails"
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            thumbnail_path = thumbnail_dir / f"{game_name}.jpg"
            
            if self._download_image(cover_url, thumbnail_path):
                print(f"✓ Downloaded thumbnail: {thumbnail_path}")
        
        # Download first screenshot (title image)
        screenshots = game_data.get("screenshots", [])
        if screenshots:
            screenshot_url = screenshots[0].get("url")
            if screenshot_url:
                # Convert to high-res URL
                screenshot_url = screenshot_url.replace("t_thumb", "t_screenshot_big")
                if not screenshot_url.startswith("http"):
                    screenshot_url = "https:" + screenshot_url
                
                # Save as title artwork
                titles_dir = self.artwork_dir / platform / "titles"
                titles_dir.mkdir(parents=True, exist_ok=True)
                title_path = titles_dir / f"{game_name}.jpg"
                
                if self._download_image(screenshot_url, title_path):
                    print(f"✓ Downloaded title art: {title_path}")
        
        return True
    
    def _download_image(self, url: str, save_path: Path) -> bool: #vers 1
        """Download image from URL
        
        Args:
            url: Image URL
            save_path: Path to save image
            
        Returns:
            True if successful
        """
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Failed to download image: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False


class IGDBSearchDialog(QDialog): #vers 2
    """Dialog for searching and downloading game artwork"""
    
    artwork_downloaded = pyqtSignal(str, str)  # game_name, platform
    
    def __init__(self, game_name: str, platform: str, igdb_downloader: IGDBDownloader, parent=None): #vers 1
        super().__init__(parent)
        self.game_name = game_name
        self.platform = platform
        self.igdb_downloader = igdb_downloader
        self.search_results = []
        
        self.setWindowTitle(f"Download Artwork - {game_name}")
        self.resize(600, 500)
        
        # Check if credentials are available
        if not self.igdb_downloader.client_id or not self.igdb_downloader.client_secret:
            QMessageBox.warning(
                self,
                "IGDB Not Configured",
                "IGDB API credentials are not configured.\n\n"
                "The developer needs to add their API key to the app,\n"
                "or you can add your own credentials to:\n"
                "config/igdb_credentials.json\n\n"
                "Get free credentials at:\n"
                "https://dev.twitch.tv/console/apps"
            )
            self.reject()
            return
        
        self._setup_ui()
        self._search_game()
    
    def _setup_ui(self): #vers 1
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"Searching IGDB for: <b>{self.game_name}</b>")
        header.setWordWrap(True)
        layout.addWidget(header)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
        # Status label
        self.status_label = QLabel("Searching...")
        layout.addWidget(self.status_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._download_selected)
        layout.addWidget(self.results_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.clicked.connect(self._download_selected)
        self.download_btn.setEnabled(False)
        button_layout.addWidget(self.download_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _search_game(self): #vers 1
        """Search for game on IGDB"""
        self.progress.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Searching IGDB...")
        
        # Search
        results = self.igdb_downloader.search_game(self.game_name, self.platform)
        
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        
        if results:
            self.search_results = results
            self.status_label.setText(f"Found {len(results)} result(s)")
            
            for game in results:
                name = game.get("name", "Unknown")
                year = game.get("first_release_date")
                if year:
                    from datetime import datetime
                    year = datetime.fromtimestamp(year).year
                    name = f"{name} ({year})"
                
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, game)
                self.results_list.addItem(item)
            
            self.download_btn.setEnabled(True)
            self.results_list.setCurrentRow(0)
        else:
            self.status_label.setText("No results found")
    
    def _download_selected(self): #vers 1
        """Download artwork for selected game"""
        current_item = self.results_list.currentItem()
        if not current_item:
            return
        
        game_data = current_item.data(Qt.ItemDataRole.UserRole)
        game_id = game_data.get("id")
        
        self.status_label.setText("Downloading artwork...")
        self.progress.setRange(0, 0)
        
        success = self.igdb_downloader.download_artwork(
            self.game_name,
            self.platform,
            game_id
        )
        
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        
        if success:
            self.status_label.setText("✓ Artwork downloaded!")
            self.artwork_downloaded.emit(self.game_name, self.platform)
            self.accept()
        else:
            self.status_label.setText("✗ Download failed")


# Credential encoder helper
def encode_credentials(client_id: str, client_secret: str): #vers 1
    """Helper to encode credentials for embedding
    
    Run this once to encode your credentials:
    >>> encode_credentials("your_id", "your_secret")
    """
    encoded_id = base64.b64encode(client_id.encode()).decode()
    encoded_secret = base64.b64encode(client_secret.encode()).decode()
    
    print("Add these to igdb_downloader.py:")
    print(f'_EMBEDDED_ID = "{encoded_id}"')
    print(f'_EMBEDDED_SECRET = "{encoded_secret}"')


# Standalone testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    if len(sys.argv) > 1 and sys.argv[1] == "encode":
        # Encode credentials
        if len(sys.argv) > 3:
            encode_credentials(sys.argv[2], sys.argv[3])
        else:
            print("Usage: python igdb_downloader.py encode <client_id> <client_secret>")
    else:
        # Test download
        app = QApplication(sys.argv)
        
        downloader = IGDBDownloader(Path.cwd() / "artwork")
        
        if len(sys.argv) > 1:
            game_name = sys.argv[1]
            platform = sys.argv[2] if len(sys.argv) > 2 else "Amiga"
            
            print(f"Searching for: {game_name} ({platform})")
            results = downloader.search_game(game_name, platform)
            
            if results:
                print(f"\nFound {len(results)} result(s):")
                for i, game in enumerate(results, 1):
                    print(f"{i}. {game.get('name')}")
                
                # Download first result
                print(f"\nDownloading artwork for: {results[0].get('name')}")
                downloader.download_artwork(game_name, platform, results[0].get("id"))
            else:
                print("No results found")
        else:
            print("Usage: python igdb_downloader.py <game_name> [platform]")
            print("   or: python igdb_downloader.py encode <client_id> <client_secret>")
