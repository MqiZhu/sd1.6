# coding: utf-8
from enum import Enum
from modules.task.zyclients import DrawClient
#
from modules.task.oss import upload_to_oss
from modules.task.log import get_logger
DrawTaskType = Enum("DrawTaskType", ("txt2img", "img2img", "single", "rmbg"))
DrawTaskStatus = Enum("DrawTaskStatus", ("New", "Fetched",
                      "Drawing", "Succ", "Failed"))


def handle_task(api, client, task_id, task_type, params):

    if task_type == DrawTaskType.txt2img.value:
        do_txt2img(api, client, task_id, params)
    if task_type == DrawTaskType.img2img.value:
        do_img2img(api, client, task_id, params)
    if task_type == DrawTaskType.single.value:
        do_single(api, client, task_id, params)
    if task_type == DrawTaskType.rmbg.value:
        do_rmbg(api, client, task_id, params)


def do_txt2img(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import StableDiffusionTxt2ImgProcessingAPI
    from modules.api.models import TextToImageResponse
    A: Api = api
    logger = get_logger()
    req = StableDiffusionTxt2ImgProcessingAPI()
    params.pop("model_id")
    real_req = req.copy(update=params)
    images, gen = api.text2img(real_req, from_fetcher=True)

    image_info = []
    succ = False
    if len(images) != 0:
        succ, image_info = upload_to_oss(images)

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "txt2img",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend:{image_info}")


def do_img2img(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import StableDiffusionImg2ImgProcessingAPI

    A: Api = api
    logger = get_logger()
    req = StableDiffusionImg2ImgProcessingAPI()
    params.pop("model_id")
    real_req = req.copy(update=params)
    images, gen = api.img2img(real_req)

    image_info = []
    succ = False
    if len(images) != 0:
        succ, image_info = upload_to_oss(images)

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "img2img",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend:{image_info}")


def do_single(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import ExtrasSingleImageRequest

    A: Api = api
    logger = get_logger()
    req = ExtrasSingleImageRequest()
    params["upscaling_resize"] = params.pop("upscale_by", None)
    real_req = req.copy(update=params)
    images, gen = api.extras_single_image(real_req)

    image_info = []
    succ = False
    if len(images) != 0:
        succ, image_info = upload_to_oss(images)

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "single",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend:{image_info}")


def do_rmbg(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import ExtrasSingleImageRequest

    A: Api = api
    logger = get_logger()
    req = ExtrasSingleImageRequest()
    real_req = req.copy(update=params)
    images, gen = api.extras_single_image(real_req)

    image_info = []
    succ = False
    if len(images) != 0:
        succ, image_info = upload_to_oss(images)

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "single",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend:{image_info}")
