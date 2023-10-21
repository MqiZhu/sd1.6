# coding:utf-8

from modules.task.config import ZY_BACK_URL, TRAINER_NAME
import modules.task.config as cfg
from modules.task.log import get_logger
import enum
import requests


class DrawClient(object):
    FecthUrl = f"{ZY_BACK_URL}/drawtask/fetch"
    UpdateStatusUrl = f"{ZY_BACK_URL}/drawtask/update"

    def __init__(self, name=TRAINER_NAME, version=cfg.WorkerVersion15) -> None:
        self.headers = {
            "--ImFromYanCheng---": "x13413413jljkljalf13343jlkajdfkla",
            "Content-Type": "application/json"
        }
        self.name = name
        self.version = version

    def call_zy_backend(self, url, data):

        data["trainer"] = self.name
        rsp = requests.post(url, headers=self.headers, json=data)

        if rsp.status_code != 200:
            get_logger().error(f"callback end failed: context={rsp.text}")
            return False, None

        rsp_data: dict = rsp.json()
        code = rsp_data.get("status_code")
        msg = rsp_data.get("status_msg")

        if code != 200:
            get_logger().error(
                f"Call Failed:url={url}, code={code}, msg={msg}")
            return False, {}

        return True, rsp_data.get("data", {})

    def fetch(self):
        return self.call_zy_backend(self.FecthUrl, {
            "version": self.version,
            "fetcher": self.name
        })

    def update_status(self, task_id: int, status: enum.Enum, result: dict):
        succ, rsp = self.call_zy_backend(self.UpdateStatusUrl, {
            "task_id": str(task_id),
            "status": status.value,
            "result": result
        })

        return succ


__lora_client = DrawClient()


def get_lora_client():
    return __lora_client
