from typing import Optional, Dict, List
from pathlib import Path
import json
import time
import subprocess
import os


class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = {}
    
    def start_monitoring(self, app_id: str):
        if app_id not in self.metrics:
            self.metrics[app_id] = []
        
        self.metrics[app_id].append({
            "start_time": time.time(),
            "end_time": None,
            "cpu_percent": [],
            "memory_mb": [],
        })
    
    def stop_monitoring(self, app_id: str):
        if app_id in self.metrics and self.metrics[app_id]:
            self.metrics[app_id][-1]["end_time"] = time.time()
    
    def record_metrics(self, app_id: str, cpu_percent: float, memory_mb: float):
        if app_id in self.metrics and self.metrics[app_id]:
            current_session = self.metrics[app_id][-1]
            current_session["cpu_percent"].append(cpu_percent)
            current_session["memory_mb"].append(memory_mb)
    
    def get_wine_process_stats(self) -> Dict:
        stats = {
            "process_count": 0,
            "total_cpu": 0.0,
            "total_memory_mb": 0.0,
            "processes": []
        }
        
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "wine" in line.lower() or "wineserver" in line:
                        parts = line.split()
                        if len(parts) >= 11:
                            try:
                                cpu = float(parts[2])
                                mem = float(parts[3])
                                pid = parts[1]
                                
                                stats["process_count"] += 1
                                stats["total_cpu"] += cpu
                                
                                stats["processes"].append({
                                    "pid": pid,
                                    "cpu_percent": cpu,
                                    "mem_percent": mem,
                                    "command": " ".join(parts[10:])
                                })
                            except (ValueError, IndexError):
                                pass
        except Exception:
            pass
        
        return stats
    
    def get_session_summary(self, app_id: str) -> Optional[Dict]:
        if app_id not in self.metrics or not self.metrics[app_id]:
            return None
        
        sessions = self.metrics[app_id]
        total_sessions = len(sessions)
        total_runtime = sum(
            (s["end_time"] - s["start_time"]) 
            for s in sessions if s["end_time"]
        )
        
        all_cpu = []
        all_memory = []
        
        for session in sessions:
            all_cpu.extend(session["cpu_percent"])
            all_memory.extend(session["memory_mb"])
        
        return {
            "total_sessions": total_sessions,
            "total_runtime_seconds": total_runtime,
            "avg_cpu_percent": sum(all_cpu) / len(all_cpu) if all_cpu else 0,
            "max_cpu_percent": max(all_cpu) if all_cpu else 0,
            "avg_memory_mb": sum(all_memory) / len(all_memory) if all_memory else 0,
            "max_memory_mb": max(all_memory) if all_memory else 0,
        }
