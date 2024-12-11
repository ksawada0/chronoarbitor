#!/usr/bin/env python

##########################################
# 
# $ python entity/perf_monitor.py '[command]'
# 
# e.g.
#     $ python entity/perf_monitor.py './run_test.sh healthcareL'
##########################################


# Standard library import
import subprocess
import psutil
import os
import sys
import time
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import pdb

if len(sys.argv) < 2:
    print('Usage: python perf_monitor.py <command>')
    sys.exit(1)

# Local import
import resources.chrono_logging as artm_logging
log = artm_logging.get_logger(__name__, json=False)



# Setup logging
logging.basicConfig(filename='performance_monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PerformanceMonitor:
    def __init__(self, command, interval=1):
        self.command = command
        self.interval = interval
        self.begin_time = None
        self.end_time = None
        self.cpu_usage_total = 0
        self.cpu_samples = 0
        self.cpu_usage_peak = 0
        self.mem_usage_total = 0
        self.mem_usage_samples = 0
        self.mem_usage_peak = 0
        self.disk_io_begin = psutil.disk_io_counters()
        self.disk_io_end = None
        self.network_io_begin = psutil.net_io_counters()
        self.network_io_end = None
        self.li_cpu_usage = []
        self.li_mem_usage = []
        
    def run(self):
        logging.info('Start performance monitor...')
        
        process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.begin_time = datetime.now()
        
        while process.poll() is None:
            self.monitor_resources()
            time.sleep(self.interval)

        self.end_time = datetime.now()
        self.disk_io_end = psutil.disk_io_counters()
        self.network_io_end = psutil.net_io_counters()
        self.log_metrics()
        logging.info('End of performance monitor...')
        logging.info('')
            
    def monitor_resources(self):
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=self.interval)
        self.li_cpu_usage.append(cpu_usage)
        self.cpu_usage_total += cpu_usage
        self.cpu_samples += 1
        self.cpu_usage_peak = max(self.cpu_usage_peak, cpu_usage)
        
        # Get memory usage
        mem = psutil.virtual_memory()
        self.li_mem_usage.append(mem.percent)
        mem_usage = mem.percent
        self.mem_usage_total += mem_usage
        self.mem_usage_samples += 1
        self.mem_usage_peak = max(self.mem_usage_peak, mem_usage)
        
        logging.info(f'cpu usage: {cpu_usage}%')
        logging.info(f'memory usage: {mem_usage}%')
        
    def log_metrics(self, is_plain_logging: bool = False, is_perf_stats: bool = False) -> dict:
        total_cpu_mean = self.cpu_usage_total / self.cpu_samples if self.cpu_samples else 0
        total_mem_mean = self.mem_usage_total / self.mem_usage_samples if self.mem_usage_samples else 0
        total_disk_io = (self.disk_io_end.read_bytes + self.disk_io_end.write_bytes) - (self.disk_io_begin.read_bytes + self.disk_io_begin.write_bytes)
        total_network_usage = (self.network_io_end.bytes_sent + self.network_io_end.bytes_recv) - (self.network_io_begin.bytes_sent + self.network_io_begin.bytes_recv)
        
        metrics = {
            "execution_time": str(self.end_time - self.begin_time),
            "cpu_usage_peak": self.cpu_usage_peak,
            "cpu_usage_mean": total_cpu_mean,
            "memory_usage_peak": self.mem_usage_peak,
            "memory_usage_mean": total_mem_mean,
            "total_disk_io": total_disk_io/1000000,
            "total_network_usage": total_network_usage/1000000
        }
        
        if is_perf_stats:
            print(metrics)
        elif is_plain_logging:
            print(f'execution time: {self.end_time - self.begin_time}')
            print(f'cpu usage - peak: {self.cpu_usage_peak} %')
            print(f'cpu usage - mean: {total_cpu_mean:.2f} %')
            print(f'memory usage - peak: {self.mem_usage_peak} %')
            print(f'memory usage - mean: {total_mem_mean:.2f} %')
            print(f'total disk i/o: {total_disk_io/1000000:.2f} MB')
            print(f'total network usage: {total_network_usage/1000000:.2f} MB')
            print(f'execution time: {self.end_time - self.begin_time}')
        else:
            logging.info(f'execution time: {self.end_time - self.begin_time}')
            logging.info(f'cpu usage - peak: {self.cpu_usage_peak} %')
            logging.info(f'cpu usage - mean: {total_cpu_mean:.2f} %')
            logging.info(f'memory usage - peak: {self.mem_usage_peak} %')
            logging.info(f'memory usage - mean: {total_mem_mean:.2f} %')
            logging.info(f'total disk i/o: {total_disk_io/1000000:.2f} MB')
            logging.info(f'total network usage: {total_network_usage/1000000:.2f} MB')
            logging.info(f'execution time: {self.end_time - self.begin_time}')
        
        return metrics
        
    def plot_metrics(self):
        time_axis = [i * self.interval for i in range(len(self.li_cpu_usage))]
        
        plt.figure(figsize=(10,5))
        plt.plot(time_axis, self.li_cpu_usage, label= ('CPU Usage (%)'))
        plt.plot(time_axis, self.li_mem_usage, label= ('Memory Usage (%)'))
        
        plt.xlabel('Time (s)')
        plt.ylabel('Usage (%)')
        plt.title('Resource Usage Over Time')
        
        plt.legend()
        plt.grid(True)
        # plt.savefig(f"usage_plot{sys.argv[1].replace(' ', '_')}.png")
        plt.savefig(f"usage_plot.png")
        plt.show()
        
        
def main():
    subsystems = [s.strip() for s in sys.argv[1].split()]
    monitor = PerformanceMonitor(sys.argv[1])
    monitor.run()
    monitor.log_metrics(is_plain_logging=True, is_perf_stats=True)
    monitor.plot_metrics()


if __name__ == '__main__': main()
    