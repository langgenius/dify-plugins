from dify_plugin import Plugin, DifyPluginEnv

import time
import logging

def run_with_retry():
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))
            plugin.run()
            break
        except Exception as e:
            logging.error(f"连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logging.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            raise e

if __name__ == '__main__':
    run_with_retry()