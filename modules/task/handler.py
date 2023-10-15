# coding: utf-8
from enum import Enum
from modules.task.zyclients import DrawClient
#

from modules.task.log import get_logger
DrawTaskType = Enum("DrawTaskType", ("txt2img", "img2img"))


def handle_task(api, client, task_type, params):

    if task_type == DrawTaskType.txt2img.value:
        do_txt2img(api, client, params)


def do_txt2img(api, client: DrawClient, params: dict):
    from modules.api.api import Api
    from modules.api.models import StableDiffusionTxt2ImgProcessingAPI
    A: Api = api
    logger = get_logger()
    req = StableDiffusionTxt2ImgProcessingAPI()
    real_req = req.copy(update=params)
    rsp = api.text2imgapi(real_req)
    logger.info(rsp)
