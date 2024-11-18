import psutil
import os
import platform
import subprocess
import json
from datetime import datetime

class SystemInterface:
    def __init__(self):
        self.system_info = self._get_initial_system_info()
        self.permissions = self._check_permissions()
        
    def _get_initial_system_info(self):
        """Sistem bilgilerini topla"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'total_memory': psutil.virtual_memory().total,
            'total_disk': psutil.disk_usage('/').total
        }
    
    def _check_permissions(self):
        """Sistem izinlerini kontrol et"""
        permissions = {
            'can_read_files': os.access('.', os.R_OK),
            'can_write_files': os.access('.', os.W_OK),
            'can_execute': os.access('.', os.X_OK)
        }
        return permissions
    
    def get_running_processes(self):
        """Çalışan işlemleri listele"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def execute_system_command(self, command, shell=False):
        """Sistem komutu çalıştır"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def monitor_resources(self):
        """Sistem kaynaklarını izle"""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'network': psutil.net_io_counters()._asdict(),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_system_snapshot(self, filename='system_snapshot.json'):
        """Sistem durumunu kaydet"""
        snapshot = {
            'system_info': self.system_info,
            'permissions': self.permissions,
            'current_resources': self.monitor_resources(),
            'running_processes': self.get_running_processes()
        }
        
        with open(filename, 'w') as f:
            json.dump(snapshot, f, indent=4, default=str)
        
        return filename
