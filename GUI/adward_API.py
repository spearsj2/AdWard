from PySide6.QtCore import QObject, Signal
import subprocess
import os
import json
import signal
import psutil
import time

class AdwardAPI(QObject):
    summary_updated = Signal(dict)
    error_occurred = Signal(str)
    status_updated = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_process = None
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.server_script = os.path.join(self.project_root, 'main', 'server.py')
        self.config_file = os.path.join(self.project_root, 'etc', 'adward.conf')
        self.blocklist_dir = os.path.join(self.project_root, 'etc', 'block_lists')
        self.allowlist_file = os.path.join(self.project_root, 'etc', 'allow_list.txt')
        
    def set_url(self, api_url: str = None) -> None:
        """Legacy method - not used in local implementation"""
        pass
        
    def fetch_status(self, api_url: str = None) -> None:
        """Check if the DNS server is running"""
        is_running = self._is_server_running()
        self.status_updated.emit(is_running)
        
    def fetch_summary(self) -> None:
        """Fetch summary data from logs"""
        try:
            summary = {
                "domains_blocked": self._count_blocklist_entries(),
                "domains_allowed": self._count_allowlist_entries(),
                "total_queries": 0 
            }
            self.summary_updated.emit(summary)
        except Exception as e:
            self.error_occurred.emit(f"Error fetching summary: {str(e)}")
    
    def toggle_status(self, enable: bool, api_url: str = None) -> None:
        """Start or stop the local DNS server"""
        try:
            if enable:
                if not self._is_server_running():
                    self._start_server()
                    time.sleep(1)  # Allow time for server to start
                    
                    if self._is_server_running():
                        self.status_updated.emit(True)
                    else:
                        self.error_occurred.emit("Failed to start the server")
                        self.status_updated.emit(False)
                else:
                    self.status_updated.emit(True)
            else:
                if self._is_server_running():
                    try:
                        self._stop_server()
                        time.sleep(1) 
                        
                        if not self._is_server_running():
                            self.status_updated.emit(False)
                        else:
                            self.error_occurred.emit("Server process still running - may need manual termination")
                            self.status_updated.emit(True)
                    except Exception as stop_error:
                        self.error_occurred.emit(f"Error stopping server: {str(stop_error)}")
                        is_running = self._is_server_running()
                        self.status_updated.emit(is_running)
                else:
                    self.status_updated.emit(False)
        except Exception as e:
            self.error_occurred.emit(f"Error toggling server: {str(e)}")
            try:
                is_running = self._is_server_running()
                self.status_updated.emit(is_running)
            except:
                self.status_updated.emit(False)
    
    def get_blocklist(self):
        """Get list of blocked domains"""
        try:
            blocked_domains = set()
            for filename in os.listdir(self.blocklist_dir):
                filepath = os.path.join(self.blocklist_dir, filename)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as file:
                        for line in file:
                            if line.startswith('0.0.0.0'):
                                domain = line.split()[1].strip()
                                blocked_domains.add(domain)
            
            allowed_domains = self._get_allowlist()
            for domain in allowed_domains:
                if domain in blocked_domains:
                    blocked_domains.remove(domain)
                    
            return list(blocked_domains)
        except Exception as e:
            self.error_occurred.emit(f"Error fetching blocklist: {str(e)}")
            return []
    
    def get_allowlist(self):
        """Get list of allowed domains"""
        return self._get_allowlist()
    
    def add_to_blocklist(self, domain):
        """Add domain to temporary blocklist"""
        try:
            custom_blocklist = os.path.join(self.blocklist_dir, "custom_blocklist.txt")
            with open(custom_blocklist, 'a') as file:
                file.write(f"0.0.0.0 {domain}\n")
            self._restart_server_if_running()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error adding to blocklist: {str(e)}")
            return False
    
    def add_to_allowlist(self, domain):
        """Add domain to allowlist"""
        try:
            with open(self.allowlist_file, 'a') as file:
                file.write(f"0.0.0.0 {domain}\n")
            self._restart_server_if_running()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error adding to allowlist: {str(e)}")
            return False
    
    def remove_from_blocklist(self, domain):
        """Remove domain from custom blocklist"""
        try:
            custom_blocklist = os.path.join(self.blocklist_dir, "custom_blocklist.txt")
            if not os.path.exists(custom_blocklist):
                return False
                
            return self.add_to_allowlist(domain)
        except Exception as e:
            self.error_occurred.emit(f"Error removing from blocklist: {str(e)}")
            return False
    
    def remove_from_allowlist(self, domain):
        """Remove domain from allowlist"""
        try:
            with open(self.allowlist_file, 'r') as file:
                lines = file.readlines()
            
            with open(self.allowlist_file, 'w') as file:
                for line in lines:
                    if not (line.startswith('0.0.0.0') and line.split()[1].strip() == domain):
                        file.write(line)
            
            self._restart_server_if_running()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error removing from allowlist: {str(e)}")
            return False
    
    def _is_server_running(self):
        """Check if the DNS server process is running"""
        if self.server_process and self.server_process.poll() is None:
            return True
            
        # Otherwise check for any python process running server.py
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                    cmdline = proc.info['cmdline']
                    if cmdline and any('server.py' in cmd for cmd in cmdline):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    
    def _start_server(self):
        """Start the DNS server process"""
        if not self._is_server_running():
            self.server_process = subprocess.Popen(['python', self.server_script])
    
    def _stop_server(self):
        """Stop the DNS server process"""
        stop_errors = []
        
        if self.server_process:
            try:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination times out
                    try:
                        self.server_process.kill()
                    except Exception as kill_error:
                        stop_errors.append(f"Kill error: {str(kill_error)}")
            except Exception as term_error:
                stop_errors.append(f"Termination error: {str(term_error)}")
            finally:
                self.server_process = None
        
        # Find and stop any other python process running server.py
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                    cmdline = proc.info['cmdline']
                    if cmdline and any('server.py' in cmd for cmd in cmdline):
                        try:
                            os.kill(proc.info['pid'], signal.SIGTERM)
                            
                            time.sleep(0.5)
                            
                            if psutil.pid_exists(proc.info['pid']):
                                try:
                                    os.kill(proc.info['pid'], signal.SIGKILL)
                                except Exception as force_error:
                                    stop_errors.append(f"Force kill error: {str(force_error)}")
                        except Exception as kill_error:
                            stop_errors.append(f"Could not terminate pid {proc.info['pid']}: {str(kill_error)}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as psutil_error:
                stop_errors.append(f"Process access error: {str(psutil_error)}")
        
        if stop_errors:
            raise Exception(f"Server stop errors: {'; '.join(stop_errors)}")
    
    def _restart_server_if_running(self):
        """Restart the server if it's currently running"""
        was_running = self._is_server_running()
        if was_running:
            self._stop_server()
            time.sleep(1)
            self._start_server()
            time.sleep(1)
    
    def _count_blocklist_entries(self):
        """Count number of domains in blocklists"""
        return len(self.get_blocklist())
    
    def _count_allowlist_entries(self):
        """Count number of domains in allowlist"""
        return len(self._get_allowlist())
    
    def _get_allowlist(self):
        """Get list of allowed domains"""
        allowed_domains = []
        try:
            if os.path.exists(self.allowlist_file):
                with open(self.allowlist_file, 'r') as file:
                    for line in file:
                        if line.startswith('0.0.0.0'):
                            domain = line.split()[1].strip()
                            allowed_domains.append(domain)
        except Exception as e:
            self.error_occurred.emit(f"Error reading allowlist: {str(e)}")
        return allowed_domains