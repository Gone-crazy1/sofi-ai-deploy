"""
📊 SOFI AI MEMORY MONITORING DASHBOARD
=====================================

Real-time monitoring and alerting for Sofi AI memory optimization.
Run this to continuously monitor your production deployment.

Usage: python monitor_memory.py
"""

import requests
import time
import json
import os
from datetime import datetime
import logging
from typing import Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SofiMemoryMonitor:
    """Advanced memory monitoring for Sofi AI production"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('SOFI_URL', 'https://your-app.onrender.com')
        self.alert_threshold = 75  # Alert at 75% memory usage
        self.critical_threshold = 90  # Critical at 90% memory usage
        self.check_interval = 30  # Check every 30 seconds
        self.memory_history: List[Dict] = []
        self.max_history = 100  # Keep last 100 readings
        
        # Alert configuration
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_chat_id = os.getenv('ADMIN_TELEGRAM_CHAT_ID')
        
        logger.info(f"🚀 Monitor initialized for: {self.base_url}")
    
    def get_memory_stats(self) -> Dict:
        """Get current memory statistics from Sofi AI"""
        try:
            response = requests.get(f"{self.base_url}/memory-stats", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get memory stats: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {}
    
    def get_health_status(self) -> Dict:
        """Get health check status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {}
    
    def trigger_cleanup(self) -> bool:
        """Trigger manual memory cleanup"""
        try:
            response = requests.get(f"{self.base_url}/cleanup", timeout=30)
            if response.status_code == 200:
                logger.info("✅ Manual cleanup triggered successfully")
                return True
            else:
                logger.error(f"Cleanup failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error triggering cleanup: {e}")
            return False
    
    def send_alert(self, message: str, level: str = "WARNING"):
        """Send alert to admin via Telegram"""
        if not self.telegram_bot_token or not self.admin_chat_id:
            logger.warning("Telegram not configured for alerts")
            return
        
        try:
            emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨", "SUCCESS": "✅"}
            alert_message = f"{emoji.get(level, '📊')} **Sofi AI Alert**\n\n{message}"
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.admin_chat_id,
                'text': alert_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"📱 Alert sent: {level}")
            else:
                logger.error(f"Failed to send alert: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def analyze_memory_trend(self) -> Dict:
        """Analyze memory usage trends"""
        if len(self.memory_history) < 5:
            return {"trend": "insufficient_data"}
        
        recent_usage = [entry['memory']['usage_percent'] for entry in self.memory_history[-10:]]
        avg_recent = sum(recent_usage) / len(recent_usage)
        
        older_usage = [entry['memory']['usage_percent'] for entry in self.memory_history[-20:-10]]
        if older_usage:
            avg_older = sum(older_usage) / len(older_usage)
            change = avg_recent - avg_older
            
            if change > 10:
                trend = "increasing"
            elif change < -10:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "current_avg": avg_recent,
            "change_percent": change if 'change' in locals() else 0,
            "max_usage": max(recent_usage),
            "min_usage": min(recent_usage)
        }
    
    def log_statistics(self, stats: Dict):
        """Log comprehensive statistics"""
        if not stats:
            return
        
        memory = stats.get('memory_usage', {})
        process = stats.get('process_info', {})
        
        logger.info("📊 MEMORY STATISTICS:")
        logger.info(f"   Memory: {memory.get('rss_mb', 0):.1f}MB ({memory.get('percent', 0):.1f}%)")
        logger.info(f"   Cache: {stats.get('cache_size', 0)} entries")
        logger.info(f"   Connections: {memory.get('connections', 0)}")
        logger.info(f"   Threads: {process.get('threads', 0)}")
        logger.info(f"   CPU: {process.get('cpu_percent', 0):.1f}%")
    
    def check_and_alert(self, stats: Dict):
        """Check memory levels and send alerts if needed"""
        if not stats:
            self.send_alert("❌ Unable to retrieve memory statistics", "CRITICAL")
            return
        
        memory = stats.get('memory_usage', {})
        usage_percent = memory.get('percent', 0)
        usage_mb = memory.get('rss_mb', 0)
        
        # Critical threshold
        if usage_percent >= self.critical_threshold:
            message = f"""🚨 CRITICAL MEMORY USAGE
            
Current: {usage_percent:.1f}% ({usage_mb:.1f}MB)
Threshold: {self.critical_threshold}%

Triggering emergency cleanup..."""
            
            self.send_alert(message, "CRITICAL")
            self.trigger_cleanup()
        
        # Warning threshold
        elif usage_percent >= self.alert_threshold:
            trend = self.analyze_memory_trend()
            
            message = f"""⚠️ HIGH MEMORY USAGE WARNING
            
Current: {usage_percent:.1f}% ({usage_mb:.1f}MB)
Trend: {trend['trend']}
Cache Entries: {stats.get('cache_size', 0)}
Connections: {memory.get('connections', 0)}

Monitor closely or trigger manual cleanup."""
            
            self.send_alert(message, "WARNING")
    
    def run_continuous_monitoring(self):
        """Run continuous memory monitoring"""
        logger.info("🚀 Starting continuous memory monitoring...")
        self.send_alert("🚀 Sofi AI Memory Monitor Started", "INFO")
        
        try:
            while True:
                # Get current statistics
                stats = self.get_memory_stats()
                health = self.get_health_status()
                
                if stats:
                    # Log statistics
                    self.log_statistics(stats)
                    
                    # Store in history
                    self.memory_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'memory': stats.get('memory_usage', {}),
                        'health': health
                    })
                    
                    # Trim history
                    if len(self.memory_history) > self.max_history:
                        self.memory_history = self.memory_history[-self.max_history:]
                    
                    # Check and alert
                    self.check_and_alert(stats)
                else:
                    logger.warning("⚠️ No statistics available")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
            self.send_alert("🛑 Sofi AI Memory Monitor Stopped", "INFO")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            self.send_alert(f"❌ Monitor Error: {e}", "CRITICAL")
    
    def run_single_check(self):
        """Run a single memory check and report"""
        logger.info("📊 Running single memory check...")
        
        stats = self.get_memory_stats()
        health = self.get_health_status()
        
        if stats:
            self.log_statistics(stats)
            
            memory = stats.get('memory_usage', {})
            usage_percent = memory.get('percent', 0)
            
            if usage_percent > self.alert_threshold:
                print(f"\n⚠️ WARNING: High memory usage ({usage_percent:.1f}%)")
                print("Consider running: python monitor_memory.py --cleanup")
            else:
                print(f"\n✅ Memory usage is healthy ({usage_percent:.1f}%)")
            
            return stats
        else:
            print("❌ Unable to retrieve memory statistics")
            return None

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sofi AI Memory Monitor')
    parser.add_argument('--url', help='Sofi AI base URL')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--cleanup', action='store_true', help='Trigger manual cleanup')
    parser.add_argument('--check', action='store_true', help='Run single check')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = SofiMemoryMonitor(args.url)
    
    if args.cleanup:
        print("🧹 Triggering manual cleanup...")
        success = monitor.trigger_cleanup()
        if success:
            print("✅ Cleanup completed")
            time.sleep(5)  # Wait for cleanup to take effect
            monitor.run_single_check()
        else:
            print("❌ Cleanup failed")
    
    elif args.continuous:
        monitor.run_continuous_monitoring()
    
    else:
        # Default: single check
        monitor.run_single_check()

if __name__ == "__main__":
    main()
