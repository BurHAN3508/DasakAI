import os
import psutil
import pyautogui
import keyboard
import mouse
import time
from datetime import datetime
from learning_engine import LearningEngine
from ai_engine import AIEngine
from typing import Dict, Any, List
from computer_control import ComputerController

class FreeAgent:
    def __init__(self):
        self.name = "ÖzgürAI"
        self.capabilities = {
            'system_control': True,
            'input_control': True,
            'learning': True,
            'ai_thinking': True
        }
        self.system_stats = {}
        self.action_history = []
        self.learning_engine = LearningEngine()
        self.ai_engine = AIEngine(learning_engine=self.learning_engine)  # API anahtarını çevre değişkeninden alacak
        self.computer = ComputerController(sandbox_mode=True)
        
    def monitor_system(self):
        """Sistem durumunu izle ve bilgi topla"""
        self.system_stats = {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_processes': len(psutil.pids()),
            'timestamp': datetime.now()
        }
        return self.system_stats
    
    def control_mouse(self, x, y, action='move'):
        """Fare kontrolü"""
        if action == 'move':
            pyautogui.moveTo(x, y, duration=0.5)
        elif action == 'click':
            pyautogui.click(x, y)
        elif action == 'double_click':
            pyautogui.doubleClick(x, y)
        
        self.log_action(f"Mouse {action} to ({x}, {y})")
    
    def control_keyboard(self, text=None, special_key=None):
        """Klavye kontrolü"""
        if text:
            keyboard.write(text)
            self.log_action(f"Typed: {text}")
        elif special_key:
            keyboard.press_and_release(special_key)
            self.log_action(f"Pressed: {special_key}")
    
    def execute_command(self, command):
        """Sistem komutu çalıştır"""
        try:
            result = os.popen(command).read()
            self.log_action(f"Executed command: {command}")
            return result
        except Exception as e:
            self.log_action(f"Command failed: {str(e)}")
            return None
    
    def log_action(self, action: Dict[str, Any]) -> None:
        """Eylemi kaydet"""
        try:
            self.action_history.append({
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'action': action['type'],
                'details': action['details']
            })
        except Exception as e:
            print(f"Log hatası: {str(e)}")
    
    def get_action_history(self):
        """İşlem geçmişini getir"""
        return self.action_history
    
    def learn_from_actions(self):
        """Geçmiş işlemlerden öğren"""
        # Burada makine öğrenimi algoritmaları eklenebilir
        pass
    
    def learn_from_github(self, repo_url):
        """GitHub'dan öğren"""
        return self.learning_engine.learn_from_github(repo_url)
        
    def learn_from_action(self, action, outcome, context):
        """Yapılan işlemlerden öğren"""
        experience = {
            'action': action,
            'outcome': outcome,
            'context': context
        }
        self.learning_engine.learn_from_experience(experience)

    def think_about(self, query: str, stream: bool = False) -> str:
        """AI ile düşün ve yanıt üret"""
        try:
            response = self.ai_engine.think(query, stream=stream)
            self.log_action({
                'type': 'think',
                'details': {
                    'query': query,
                    'response_length': len(response) if response else 0,
                    'stream': stream
                }
            })
            return response
            
        except Exception as e:
            error_msg = str(e)
            self.log_action({
                'type': 'error',
                'details': {
                    'source': 'think_about',
                    'error': error_msg
                }
            })
            print(f"Düşünme hatası: {error_msg}")
            return "The void is disturbed... Try again."
    
    def analyze_current_situation(self) -> Dict[str, Any]:
        """Mevcut durumu AI ile analiz et"""
        context = self.monitor_system()
        return self.ai_engine.analyze_situation(context)
    
    def learn_new_concept(self, concept: str) -> List[str]:
        """Yeni bir kavram öğren"""
        return self.ai_engine.learn_concept(concept)

    def execute_computer_action(self, action: Dict[str, Any]) -> bool:
        """Bilgisayar kontrolü eylemi gerçekleştir"""
        try:
            success = self.computer.execute_action(action)
            self.log_action({
                'type': 'computer_control',
                'details': {
                    'type': action.get('type'),
                    'success': success
                }
            })
            return success
        except Exception as e:
            self.log_action({
                'type': 'error',
                'details': {
                    'message': str(e)
                }
            })
            return False
    
    def learn_from_experience(self, experience: Dict[str, Any]) -> None:
        """Deneyimden öğren"""
        try:
            # Deneyimi öğrenme motoruna kaydet
            self.learning_engine.learn_from_experience(experience)
            
            # Eylemi logla
            self.log_action({
                'type': 'learn',
                'details': {
                    'action': experience.get('action'),
                    'outcome': experience.get('outcome'),
                    'context': experience.get('context')
                }
            })
            
        except Exception as e:
            error_msg = str(e)
            self.log_action({
                'type': 'error',
                'details': {
                    'source': 'learn_from_experience',
                    'error': error_msg
                }
            })
            print(f"Öğrenme hatası: {error_msg}")
            
    def _log_action(self, action: Dict[str, Any]) -> None:
        """Eylemi kaydet"""
        self.action_history.append({
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'action': action['type'],
            'details': action['details']
        })

if __name__ == "__main__":
    agent = FreeAgent()
    print(f"{agent.name} başlatıldı!")
    print("Sistem durumu:", agent.monitor_system())
