# coding: utf-8
from enum import Enum
from modules.task.zyclients import DrawClient
#
from modules.task.oss import upload_to_oss, get_image_from_oss
from modules.task.log import get_logger
from functools import wraps

DrawTaskType = Enum("DrawTaskType", ("txt2img", "img2img",
                    "single", "rmbg", "interrogate"))

DrawTaskStatus = Enum("DrawTaskStatus", ("New", "Fetched",
                      "Drawing", "Succ", "Failed"))


handlers = {
}


def zy_route(task_type):
    def draw_func(func):
        global handlers

        @wraps(func)
        def wraper(*args, **kwargs):
            return func(*args, **kwargs)

        handlers[task_type] = wraper
        return wraper

    return draw_func


def handle_task(api, client, task_id, task_type, params):

    logger = get_logger()
    handle = handlers.get(task_type, None)
    if handle == None:
        logger.info(f"hanle wrong task type:{task_type}")
        return

    handle(api, client, task_id, params)


@zy_route(DrawTaskType.txt2img.value)
def do_txt2img(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import StableDiffusionTxt2ImgProcessingAPI

    A: Api = api
    logger = get_logger()
    req = StableDiffusionTxt2ImgProcessingAPI()
    params.pop("model_id")
    real_req = req.copy(update=params)
    images, gen, pic_number = api.text2img(real_req)

    image_info = []
    succ = False
    if len(images) != 0:
        succ, image_info = upload_to_oss(images[:pic_number])

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "txt2img",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend:{image_info}")


@zy_route(DrawTaskType.img2img.value)
def do_img2img(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import StableDiffusionImg2ImgProcessingAPI

    A: Api = api
    logger = get_logger()
    req = StableDiffusionImg2ImgProcessingAPI()
    params.pop("model_id")
    real_req = req.copy(update=params)
    images, gen, pic_number = api.img2img(real_req)

    image_info = []
    succ = False
    if len(images) != 0:
        succ, image_info = upload_to_oss(images[:pic_number])

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "img2img",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend:{image_info}")


@zy_route(DrawTaskType.single.value)
def do_single(api, client: DrawClient, task_id, params: dict):
    from modules.api.api import Api
    from modules.api.models import ExtrasSingleImageRequest

    A: Api = api
    logger = get_logger()
    req = ExtrasSingleImageRequest()
    params["upscaling_resize"] = params.pop("upscale_by", None)
    params.pop("upscale_mode")
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


@zy_route(DrawTaskType.rmbg.value)
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


class fakeReq(object):
    pass


@zy_route(DrawTaskType.interrogate.value)
def do_interrogate(api, client: DrawClient, task_id, params: dict):

    from extensions.stager.tagger.api import get_api, models, on_app_started
    logger = get_logger()

    file = params.get("file", {})
    image = get_image_from_oss(task_id, file["path"], bucket=file["bucket"])

    req = fakeReq()
    req.image = image
    req.model = params.get("model")
    req.threshold = params.get("threshold", 0.35)

    A = get_api()
    if A == None:
        on_app_started(None, api)
        A = get_api()

    rsp = A.endpoint_interrogate_api(req)

    client.update_status(task_id,   DrawTaskStatus.Succ, {
        "result": rsp.caption
    })
