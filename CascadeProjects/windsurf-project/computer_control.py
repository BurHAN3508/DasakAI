import pyautogui
import webbrowser
import time
from typing import Dict, Any

class ComputerController:
    def __init__(self, sandbox_mode: bool = True):
        self.sandbox_mode = sandbox_mode
        pyautogui.FAILSAFE = True
        self.allowed_sites = ['google.com', 'github.com', 'stackoverflow.com']
        
    def browse(self, url: str) -> bool:
        """Güvenli web tarayıcı kontrolü"""
        try:
            # URL güvenlik kontrolü
            if self.sandbox_mode:
                domain = url.split('/')[2] if '://' in url else url.split('/')[0]
                if not any(site in domain for site in self.allowed_sites):
                    print(f"Uyarı: {domain} sandbox modunda erişilemez!")
                    return False
            
            webbrowser.open(url)
            return True
            
        except Exception as e:
            print(f"Tarayıcı hatası: {str(e)}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Güvenli metin yazma"""
        try:
            if len(text) > 100 and self.sandbox_mode:  # Uzun metinleri sınırla
                print("Uyarı: Çok uzun metin!")
                return False
                
            pyautogui.typewrite(text)
            return True
            
        except Exception as e:
            print(f"Yazma hatası: {str(e)}")
            return False
    
    def click(self, x: int, y: int) -> bool:
        """Güvenli tıklama"""
        try:
            if self.sandbox_mode:
                # Ekran sınırlarını kontrol et
                screen_width, screen_height = pyautogui.size()
                if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                    print("Uyarı: Ekran sınırları dışında!")
                    return False
            
            pyautogui.click(x, y)
            return True
            
        except Exception as e:
            print(f"Tıklama hatası: {str(e)}")
            return False
    
    def search_google(self, query: str) -> bool:
        """Google'da güvenli arama"""
        try:
            if self.sandbox_mode and len(query) > 50:  # Uzun sorguları sınırla
                print("Uyarı: Çok uzun arama sorgusu!")
                return False
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            return self.browse(search_url)
            
        except Exception as e:
            print(f"Arama hatası: {str(e)}")
            return False
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """Eylem türüne göre kontrol"""
        try:
            action_type = action.get('type', '').lower()
            
            if action_type == 'click':
                return self.click(action['x'], action['y'])
                
            elif action_type == 'type':
                return self.type_text(action['text'])
                
            elif action_type == 'browse':
                return self.browse(action['url'])
                
            elif action_type == 'search':
                return self.search_google(action['query'])
                
            else:
                print(f"Bilinmeyen eylem türü: {action_type}")
                return False
                
        except Exception as e:
            print(f"Eylem hatası: {str(e)}")
            return False
