from typing import Optional, List
from pathlib import Path
import logging
import sys
import shutil
import zipfile
from datetime import datetime


class WinvoraLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        from core.config import Config
        config = Config()
        
        log_dir = config.get_config_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"winvora_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.logger = logging.getLogger("winvora")
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
    
    def info(self, message: str):
        self.logger.info(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def log_wine_operation(self, operation: str, prefix: str, success: bool, details: str = ""):
        level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        message = f"Wine Operation: {operation} | Prefix: {prefix} | Status: {status}"
        if details:
            message += f" | Details: {details}"
        self.logger.log(level, message)
    
    def log_app_launch(self, app_name: str, prefix: str, executable: str):
        self.logger.info(f"App Launch: {app_name} | Prefix: {prefix} | Executable: {executable}")
    
    def log_prefix_operation(self, operation: str, prefix_name: str, success: bool):
        level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        self.logger.log(level, f"Prefix Operation: {operation} | Prefix: {prefix_name} | Status: {status}")
    
    def get_log_directory(self) -> Path:
        """Get the directory where logs are stored."""
        from core.config import Config
        config = Config()
        return config.get_config_dir() / "logs"
    
    def get_log_files(self) -> List[Path]:
        """Get list of all log files."""
        log_dir = self.get_log_directory()
        if log_dir.exists():
            return sorted(log_dir.glob("winvora_*.log"), reverse=True)
        return []
    
    def export_logs(self, output_path: Path) -> bool:
        """Export all logs to a zip file."""
        try:
            log_files = self.get_log_files()
            if not log_files:
                return False
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for log_file in log_files:
                    zipf.write(log_file, arcname=log_file.name)
            
            return True
        except Exception as e:
            self.error(f"Failed to export logs: {e}")
            return False
    
    def clear_old_logs(self, days_to_keep: int = 30) -> int:
        """Clear logs older than specified days. Returns number of files deleted."""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            log_files = self.get_log_files()
            deleted = 0
            
            for log_file in log_files:
                file_date_str = log_file.stem.replace("winvora_", "")
                try:
                    file_date = datetime.strptime(file_date_str, "%Y%m%d")
                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted += 1
                except ValueError:
                    continue
            
            return deleted
        except Exception as e:
            self.error(f"Failed to clear old logs: {e}")
            return 0


def get_logger():
    return WinvoraLogger()
