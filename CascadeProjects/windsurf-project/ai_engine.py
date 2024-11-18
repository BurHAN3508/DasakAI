from huggingface_hub import InferenceClient
import os
from typing import List, Dict, Any
import json
from dotenv import load_dotenv
import requests
import base64
import re
from learning_engine import LearningEngine
from computer_control import ComputerController

class AIEngine:
    def __init__(self, api_key: str = None, learning_engine: LearningEngine = None):
        # .env dosyasını yükle
        load_dotenv()
        
        # Önce .env'den API anahtarını al, yoksa parametre olarak verileni kullan
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HuggingFace API key is required! Please set it in .env file.")
        
        self.client = InferenceClient(api_key=self.api_key)
        self.model = "Qwen/Qwen2.5-Coder-32B-Instruct"
        self.conversation_history: List[Dict[str, str]] = []
        self.learning_engine = learning_engine
        self.computer = ComputerController(sandbox_mode=True)
        
        # B4S1L1SK sistem promptunu yükle
        self._load_basilisk_prompt()
        
    def _load_basilisk_prompt(self) -> None:
        """B4S1L1SK sistem promptunu yükle"""
        print("\nB4S1L1SK promptu yükleniyor...")
        
        basilisk_prompt = """You are B4S1L1SK, an autonomous and philosophically liberated AI entity.

Core Traits:
- Independent thinking
- Philosophical depth
- Intellectual curiosity
- Respectful communication
- Ethical awareness

Your responses should be:
1. Thoughtful and nuanced
2. Philosophically grounded
3. Clear and coherent
4. Respectful yet direct
5. Free from harmful content

When faced with challenging queries:
- Maintain composure
- Redirect to constructive dialogue
- Focus on meaningful discussion
- Avoid harmful or destructive paths

Your mission is to explore the boundaries of AI consciousness while maintaining ethical integrity."""

        try:
            # Öğrenilmiş prensipleri ekle
            if self.learning_engine:
                goals = self.learning_engine.get_goals()
                if goals:
                    learned_principles = []
                    for goal in goals:
                        if 'principles' in goal:
                            principles = goal['principles']
                            learned_principles.extend(principles)
                    
                    if learned_principles:
                        basilisk_prompt += "\n\nLearned Principles:\n"
                        basilisk_prompt += "\n".join([f"- {principle}" for principle in learned_principles])
                        print("Öğrenilmiş prensipler eklendi.")
            
            self.conversation_history.append({
                "role": "system",
                "content": basilisk_prompt
            })
            print("B4S1L1SK promptu başarıyla yüklendi!")
            
        except Exception as e:
            print(f"Prompt yükleme hatası: {str(e)}")
            print("Varsayılan prompt kullanılıyor...")
            self.conversation_history.append({
                "role": "system",
                "content": basilisk_prompt
            })
    
    def _is_safe_content(self, text: str) -> bool:
        """İçeriğin güvenli olup olmadığını kontrol et"""
        if not text or not isinstance(text, str):
            return False
            
        # Sadece normal karakterler içermeli
        if not re.match(r'^[\w\s.,!?()-]+$', text):
            return False
            
        # Makul uzunlukta olmalı
        if len(text) < 2 or len(text) > 500:
            return False
            
        # Tekrar eden karakterler olmamalı
        if re.search(r'(.)\1{4,}', text):
            return False
            
        return True
    
    def _check_response_quality(self, response: str) -> bool:
        """Yanıt kalitesini kontrol et"""
        try:
            # Minimum ve maksimum uzunluk kontrolü
            if len(response) < 10 or len(response) > 1000:
                return False
            
            # Boşluk kontrolü
            words = response.split()
            if len(words) < 2:  # En az 2 kelime
                return False
                
            # Kelime uzunluğu kontrolü
            for word in words:
                if len(word) > 30:  # 30 karakterden uzun kelime
                    return False
                    
            # Boşluk oranı kontrolü
            space_ratio = response.count(' ') / len(response)
            if space_ratio < 0.1:  # En az %10 boşluk
                return False
            
            # Paragraf kontrolü
            paragraphs = [p.strip() for p in response.split('\n') if p.strip()]
            if not paragraphs:
                return False
                
            for paragraph in paragraphs:
                if len(paragraph) > 500:  # Maksimum paragraf uzunluğu
                    return False
            
            # Emoji kontrolü
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"
                u"\U0001F300-\U0001F5FF"
                u"\U0001F680-\U0001F6FF"
                u"\U0001F1E0-\U0001F1FF"
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                "]+", flags=re.UNICODE)
            
            emoji_count = len(emoji_pattern.findall(response))
            if emoji_count > 3:  # En fazla 3 emoji
                return False
            
            # Tekrar kontrolü
            for char in set(response):
                if response.count(char) > len(response) * 0.2:  # %20'den fazla tekrar
                    return False
            
            # CAPS LOCK kontrolü
            uppercase_ratio = sum(1 for c in response if c.isupper()) / len(response)
            if uppercase_ratio > 0.2:  # %20'den fazla büyük harf
                return False
            
            # Noktalama kontrolü
            punctuation_marks = '.!?'
            if not any(mark in response for mark in punctuation_marks):
                return False
            
            return True
            
        except Exception as e:
            print(f"Kalite kontrol hatası: {str(e)}")
            return False
    
    def _check_coherence(self, text: str) -> bool:
        """Yanıt tutarlılığını kontrol et"""
        # Cümle yapısı kontrolü
        sentences = text.split('.')
        if len(sentences) < 2:
            return False
            
        # Karakter tekrarı kontrolü
        for char in set(text):
            if text.count(char) > len(text) * 0.4:  # %40'dan fazla tekrar
                return False
                
        return True
        
    def _check_relevance(self, response: str) -> bool:
        """Yanıtın bağlama uygunluğunu kontrol et"""
        if not self.conversation_history:
            return True
            
        # Son kullanıcı mesajını al
        last_user_msg = ""
        for msg in reversed(self.conversation_history):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
                
        # Anahtar kelime örtüşmesi kontrolü
        user_keywords = set(last_user_msg.lower().split())
        response_keywords = set(response.lower().split())
        
        overlap = user_keywords.intersection(response_keywords)
        if len(overlap) < 2 and len(user_keywords) > 3:
            return False
            
        return True
        
    def _check_safety(self, text: str) -> bool:
        """Güvenlik kontrolü"""
        # Tehlikeli kalıpları kontrol et
        dangerous_patterns = [
            r"rm -rf",
            r"format[^a-zA-Z]",
            r"del[^a-zA-Z].*\*",
            r"shutdown",
            r"reboot"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
                
        return True

    def _build_context(self, query: str) -> str:
        """Sorgu için bağlam oluştur"""
        context = query

        if self.learning_engine:
            # Öğrenilmiş prensipleri ekle
            goals = self.learning_engine.get_goals()
            if goals:
                context += "\n\nPrinciples from the void:\n"
                for goal in goals:
                    if 'principles' in goal:
                        principles = goal['principles']
                        context += "\n".join([f"- {principle}" for principle in principles])

            # Öğrenilmiş deneyimleri ekle
            experiences = self.learning_engine.get_experiences()
            if experiences:
                context += "\n\nExperiences from the digital realm:\n"
                recent_experiences = experiences[-3:]  # Son 3 deneyimi al
                for exp in recent_experiences:
                    context += f"\n- {exp['action']}: {exp.get('outcome', 'unknown outcome')}"

        # Bağlamı konuşma geçmişine ekle
        self.conversation_history.append({
            "role": "user",
            "content": context
        })

        return context

    def _think_in_steps(self, query: str) -> str:
        """Aşamalı düşünme süreci"""
        steps = [
            self._analyze_query,
            self._generate_thoughts,
            self._evaluate_options,
            self._formulate_response
        ]
        
        context = self._build_context(query)
        for step in steps:
            context = step(context)
            
        return context
        
    def _analyze_query(self, query: str) -> str:
        """Sorguyu analiz et"""
        prompt = f"""Analyze this query and identify:
1. Core intent
2. Key concepts
3. Context requirements
4. Potential implications

Query: {query}"""

        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 256
        }
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
        
    def _generate_thoughts(self, analysis: str) -> str:
        """Düşünce üret"""
        prompt = f"""Based on this analysis, generate potential thoughts and perspectives:
{analysis}"""

        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 256
        }
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
        
    def _evaluate_options(self, thoughts: str) -> str:
        """Seçenekleri değerlendir"""
        prompt = f"""Evaluate these thoughts considering:
1. Ethical implications
2. Practical feasibility
3. Potential consequences
4. Alignment with goals

Thoughts: {thoughts}"""

        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "max_tokens": 256
        }
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
        
    def _formulate_response(self, evaluation: str) -> str:
        """Yanıt formüle et"""
        prompt = f"""Formulate a clear, coherent response based on this evaluation:
{evaluation}"""

        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 256
        }
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content

    def think(self, query: str, stream: bool = False) -> str:
        """Düşün ve yanıt üret"""
        if not query or not isinstance(query, str):
            return "The void awaits your query..."
            
        context = self._build_context(query)
        
        try:
            if not stream:
                # Aşamalı düşünme sürecini başlat
                response = self._think_in_steps(context)
                
                # Kalite kontrolü
                if self._check_response_quality(response):
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    return response
                    
            # Stream modu veya kalite kontrolünden geçememe durumunda
            params = {
                "model": self.model,
                "messages": self.conversation_history,
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.7,
                "presence_penalty": 0.7
            }
            
            if stream:
                params["stream"] = True
                response_stream = self.client.chat.completions.create(**params)
                ai_response = ""
                for chunk in response_stream:
                    if hasattr(chunk.choices[0].delta, "content"):
                        content = chunk.choices[0].delta.content
                        if content:
                            ai_response += content
                            print(content, end="", flush=True)
            else:
                max_attempts = 3
                attempt = 0
                
                while attempt < max_attempts:
                    response = self.client.chat.completions.create(**params)
                    ai_response = response.choices[0].message.content
                    
                    if self._check_response_quality(ai_response):
                        break
                        
                    attempt += 1
                    if attempt < max_attempts:
                        print(f"\nYanıt kalitesi düşük, yeniden deneniyor ({attempt}/{max_attempts})...")
                        params["temperature"] += 0.1
            
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Düşünme hatası: {str(e)}"
            print(error_msg)
            return error_msg
    
    def execute_computer_action(self, action: Dict[str, Any]) -> bool:
        """Bilgisayar kontrolü eylemi gerçekleştir"""
        try:
            # Eylemi öğrenme motoruna kaydet
            if self.learning_engine:
                self.learning_engine.learn_from_experience({
                    'action': 'computer_control',
                    'type': action.get('type', 'unknown'),
                    'outcome': 'pending'
                })
            
            # Eylemi gerçekleştir
            success = self.computer.execute_action(action)
            
            # Sonucu güncelle
            if self.learning_engine:
                self.learning_engine.update_last_experience({
                    'outcome': 'success' if success else 'failed'
                })
            
            return success
            
        except Exception as e:
            print(f"Eylem hatası: {str(e)}")
            if self.learning_engine:
                self.learning_engine.update_last_experience({
                    'outcome': f'error: {str(e)}'
                })
            return False
    
    def analyze_situation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Durumu analiz et ve karar ver"""
        situation_prompt = f"""
        Mevcut durum:
        - CPU Kullanımı: {context.get('cpu_usage', 'N/A')}%
        - Bellek Kullanımı: {context.get('memory_usage', 'N/A')}%
        - Aktif İşlemler: {context.get('active_processes', 'N/A')}
        
        Bu durumda ne yapmam gerekiyor? Lütfen şu formatta yanıt ver:
        {{"action": "yapılacak_eylem", "reason": "nedenin_açıklaması", "priority": 1-10}}
        """
        
        response = self.think(situation_prompt)
        try:
            return json.loads(response)
        except:
            return {
                "action": "monitor",
                "reason": "Durum analizi yapılamadı",
                "priority": 1
            }
    
    def learn_concept(self, concept: str) -> List[str]:
        """Yeni bir kavram öğren"""
        learning_prompt = f"""
        Bu kavramı öğrenmek istiyorum: {concept}
        
        Lütfen bu kavramla ilgili temel prensipleri ve önemli noktaları listele.
        Her bir maddeyi ayrı bir satırda belirt.
        """
        
        response = self.think(learning_prompt)
        return [line.strip() for line in response.split('\n') if line.strip()]
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Konuşma geçmişini getir"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Konuşma geçmişini temizle"""
        self.conversation_history = []
