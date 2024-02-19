# coding: utf-8
from __future__ import annotations

import threading
from modules.task.zyclients import DrawClient
import time
from modules.task.log import get_logger
from modules.task.handler import handle_task


def fetch_and_dispatch(api, name, version, base_url):
    time.sleep(1)
    client = DrawClient(name=name, version=version, base_url=base_url)
    logger = get_logger()

    logger.info("fetch_and_dispatch")
    while True:
        suc, data = client.fetch()
        if not suc:
            logger.info("get task failed:{data}")
            time.sleep(1)
            continue

        has_task = data.get("has_task", False)
        wait = data.get("wait", 1)
        if not has_task:
            time.sleep(1)
            logger.info("no task")
            continue

        task = data.get("task")
        task_id = task.get("task_id")
        params = task["real_param"]
        task_type = task["task_type"]
        owner = task["owner"]
        try:
            handle_task(api, client, task_id, task_type, params, owner)
        except Exception as e:
            import traceback
            traceback.print_exc()

        logger.info(f"handler_task:{task_id}")


def RunTaskFetcher(api, name, version, base_url):
    t = threading.Thread(target=fetch_and_dispatch, args=(api, name, version, base_url))
    t.daemon = True
    t.start()
    return t
