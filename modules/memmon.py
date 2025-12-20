import threading
import time
from collections import defaultdict

import torch


class MemUsageMonitor(threading.Thread):
    run_flag = None
    device = None
    disabled = False
    opts = None
    data = None

    def __init__(self, name, device, opts):
        threading.Thread.__init__(self)
        self.name = name
        self.device = device
        self.opts = opts

        self.daemon = True
        self.run_flag = threading.Event()
        self.data = defaultdict(int)

        try:
            self.cuda_mem_get_info()
            torch.cuda.memory_stats(self.device)
        except Exception as e:  # AMD or whatever
            print(f"Warning: caught exception '{e}', memory monitor disabled")
            self.disabled = True

    def cuda_mem_get_info(self):
        index = self.device.index if self.device.index is not None else torch.cuda.current_device()
        try:
            return torch.cuda.mem_get_info(index)
        except RuntimeError as e:
            # CUDAメモリ不足エラーの場合、デフォルト値を返す
            if "out of memory" in str(e).lower():
                # メモリ情報が取得できない場合は、0を返す（エラーを回避）
                return (0, 0)
            raise

    def run(self):
        if self.disabled:
            return

        while True:
            self.run_flag.wait()

            torch.cuda.reset_peak_memory_stats()
            self.data.clear()

            if self.opts.memmon_poll_rate <= 0:
                self.run_flag.clear()
                continue

            try:
                self.data["min_free"] = self.cuda_mem_get_info()[0]
            except Exception:
                # メモリ情報が取得できない場合は、デフォルト値を設定
                self.data["min_free"] = 0

            while self.run_flag.is_set():
                try:
                    free, total = self.cuda_mem_get_info()
                    if free > 0 and total > 0:  # 有効な値の場合のみ更新
                        self.data["min_free"] = min(self.data["min_free"], free)
                except Exception:
                    # メモリ情報が取得できない場合は、監視を続行
                    pass

                time.sleep(1 / self.opts.memmon_poll_rate)

    def dump_debug(self):
        print(self, 'recorded data:')
        try:
            for k, v in self.read().items():
                print(k, -(v // -(1024 ** 2)))
        except Exception as e:
            print(f"Error reading memory data: {e}")

        print(self, 'raw torch memory stats:')
        try:
            tm = torch.cuda.memory_stats(self.device)
            for k, v in tm.items():
                if 'bytes' not in k:
                    continue
                print('\t' if 'peak' in k else '', k, -(v // -(1024 ** 2)))
        except Exception as e:
            print(f"Error getting torch memory stats: {e}")

        try:
            print(torch.cuda.memory_summary())
        except Exception as e:
            print(f"Error getting memory summary: {e}")

    def monitor(self):
        self.run_flag.set()

    def read(self):
        if not self.disabled:
            try:
                free, total = self.cuda_mem_get_info()
                self.data["free"] = free
                self.data["total"] = total
            except Exception:
                # メモリ情報が取得できない場合は、既存の値を保持
                if "free" not in self.data:
                    self.data["free"] = 0
                if "total" not in self.data:
                    self.data["total"] = 0

            try:
                torch_stats = torch.cuda.memory_stats(self.device)
                self.data["active"] = torch_stats["active.all.current"]
                self.data["active_peak"] = torch_stats["active_bytes.all.peak"]
                self.data["reserved"] = torch_stats["reserved_bytes.all.current"]
                self.data["reserved_peak"] = torch_stats["reserved_bytes.all.peak"]
                total = self.data.get("total", 0)
                self.data["system_peak"] = total - self.data.get("min_free", 0)
            except Exception:
                # メモリ統計が取得できない場合は、デフォルト値を設定
                if "active" not in self.data:
                    self.data["active"] = 0
                if "active_peak" not in self.data:
                    self.data["active_peak"] = 0
                if "reserved" not in self.data:
                    self.data["reserved"] = 0
                if "reserved_peak" not in self.data:
                    self.data["reserved_peak"] = 0
                if "system_peak" not in self.data:
                    self.data["system_peak"] = 0

        return self.data

    def stop(self):
        self.run_flag.clear()
        return self.read()
