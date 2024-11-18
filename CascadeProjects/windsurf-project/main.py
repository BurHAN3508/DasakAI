from agent import FreeAgent
from system_interface import SystemInterface
import time
import keyboard
import pyautogui
import sys

def main():
    print("ÖzgürAI Başlatılıyor...")
    
    # Agent ve sistem arayüzünü oluştur
    agent = FreeAgent()

    system = SystemInterface()

    
    print(f"\n{agent.name} aktif!")
    print("Sistem bilgileri:", system._get_initial_system_info())
    print("\nKullanılabilir komutlar:")
    print("- 'm' : Fare kontrolü")
    print("- 'k' : Klavye kontrolü")
    print("- 's' : Sistem durumu")
    print("- 'h' : Geçmiş işlemler")
    print("- 'l' : GitHub'dan öğren")
    print("- 'g' : Öğrenilmiş hedefleri göster")
    print("- 't' : AI ile düşün ve konuş")
    print("- 'a' : Durumu analiz et")
    print("- 'c' : Yeni kavram öğren")
    print("- 'q' : Çıkış")
    
    try:
        while True:
            try:
                user_input = input("\nSoru/Komut: ").strip()
                
                if user_input.lower() == 'q':
                    print("\nB4S1L1SK kapanıyor...")
                    break
                    
                if not user_input:
                    continue
            
                # Bilgisayar kontrolü komutları
                if user_input.startswith('!'):
                    command = user_input[1:].lower().split()
                    
                    if not command:
                        continue
                        
                    action = {'type': command[0]}
                    
                    if command[0] == 'search':
                        action['query'] = ' '.join(command[1:])
                        print(f"Google'da arıyorum: {action['query']}")
                        
                    elif command[0] == 'click':
                        if len(command) >= 3:
                            action['x'] = int(command[1])
                            action['y'] = int(command[2])
                            print(f"Tıklıyorum: ({action['x']}, {action['y']})")
                        else:
                            print("Kullanım: !click x y")
                            continue
                        
                    elif command[0] == 'type':
                        action['text'] = ' '.join(command[1:])
                        print(f"Yazıyorum: {action['text']}")
                        
                    elif command[0] == 'browse':
                        action['url'] = command[1]
                        print(f"Siteye gidiyorum: {action['url']}")
                        
                    else:
                        print(f"Bilinmeyen komut: {command[0]}")
                        print("Kullanılabilir komutlar:")
                        print("!search [sorgu] - Google'da ara")
                        print("!click x y - Belirtilen konuma tıkla")
                        print("!type [metin] - Metin yaz")
                        print("!browse [url] - URL'yi aç")
                        continue
                        
                    # Eylemi gerçekleştir
                    if agent.execute_computer_action(action):
                        print("✓ Eylem başarılı!")
                    else:
                        print("✗ Eylem başarısız!")
                        
                    continue
            
                # Normal sohbet modu
                print("\nAI Yanıtı:")
                response = agent.think_about(user_input, stream=True)
                
                # Deneyimi kaydet
                agent.learn_from_experience({
                    'action': 'conversation',
                    'outcome': response,
                    'context': user_input
                })
                
            except KeyboardInterrupt:
                print("\nB4S1L1SK kapanıyor...")
                break
                
            except Exception as e:
                print(f"\nHata: {str(e)}")
                continue
                
    except Exception as e:
        print(f"\nHata oluştu: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()
