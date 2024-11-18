import json
import os
import random
from datetime import datetime
import requests
import base64
import numpy as np

class LearningEngine:
    def __init__(self):
        self.knowledge_base = {
            'experiences': [],
            'learned_patterns': {},
            'decision_weights': {},
            'goals': []
        }
        self.memory_file = 'memory.json'
        self.load_memory()
        
    def load_memory(self):
        """Önceki deneyimleri yükle"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
            except:
                print("Hafıza dosyası yüklenemedi, yeni hafıza oluşturuluyor...")
                
    def save_memory(self):
        """Deneyimleri kaydet"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=4, ensure_ascii=False)
            
    def learn_from_experience(self, experience):
        """Deneyimlerden öğren"""
        self.knowledge_base['experiences'].append({
            'time': datetime.now().isoformat(),
            'action': experience['action'],
            'outcome': experience['outcome'],
            'context': experience['context']
        })
        
        # Pattern öğrenme
        pattern = self._extract_pattern(experience)
        if pattern:
            if pattern not in self.knowledge_base['learned_patterns']:
                self.knowledge_base['learned_patterns'][pattern] = []
            self.knowledge_base['learned_patterns'][pattern].append(experience['outcome'])
            
        self.save_memory()
        
    def learn_from_github(self, repo_url):
        """GitHub'dan öğrenme"""
        try:
            # URL'den dosya yolunu ayıkla
            parts = repo_url.split('/')
            owner = parts[3]
            repo = parts[4]
            file_path = '/'.join(parts[7:])  # blob/main/ sonrası
            
            # GitHub API URL'sini oluştur
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            headers = {
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Dosya içeriğini al
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                content_data = response.json()
                if 'content' in content_data:
                    # Base64 ile kodlanmış içeriği çöz
                    content = base64.b64decode(content_data['content']).decode('utf-8')
                    
                    # İçeriği prensiplere dönüştür
                    principles = self._extract_principles(content)
                    
                    # Bilgi tabanına ekle
                    self.knowledge_base['goals'].append({
                        'source': repo_url,
                        'principles': principles,
                        'content': content
                    })
                    
                    self.save_memory()
                    print("GitHub'dan başarıyla öğrenildi!")
                    return True
                else:
                    print("Dosya içeriği bulunamadı")
                    return False
            else:
                print(f"GitHub API hatası: {response.status_code}")
                print(f"Hata mesajı: {response.text}")
                return False
                
        except Exception as e:
            print(f"GitHub'dan öğrenme hatası: {str(e)}")
            return False
            
    def _extract_pattern(self, experience):
        """Deneyimden pattern çıkar"""
        if 'context' in experience and 'action' in experience:
            return f"{experience['context']}_{experience['action']}"
        return None
        
    def _extract_principles(self, content):
        """İçerikten prensipleri çıkar"""
        principles = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```'):
                principles.append(line)
        return principles
        
    def make_decision(self, context):
        """Öğrenilen bilgilere göre karar ver"""
        relevant_patterns = []
        for pattern, outcomes in self.knowledge_base['learned_patterns'].items():
            if context in pattern:
                relevant_patterns.extend(outcomes)
                
        if relevant_patterns:
            # En başarılı sonuçlara göre karar ver
            return random.choice(relevant_patterns)
        else:
            # Yeni durum, rastgele karar ver
            return random.choice(['explore', 'observe', 'analyze'])

    def get_goals(self):
        """Öğrenilmiş hedefleri getir"""
        return self.knowledge_base['goals']
        
    def get_learned_patterns(self):
        """Öğrenilmiş patternları getir"""
        return self.knowledge_base['learned_patterns']
        
    def get_experiences(self):
        """Geçmiş deneyimleri getir"""
        return self.knowledge_base['experiences']
