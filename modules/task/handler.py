# coding: utf-8
from enum import Enum
from io import BytesIO
import base64

from modules.task.zyclients import DrawClient
from modules.task.watermask import batch_watermark
from modules.task.oss import upload_to_oss, get_image_from_oss, upload_to_puzzle
from modules.task.log import get_logger
from functools import wraps

DrawTaskType = Enum("DrawTaskType", ("txt2img", "img2img",
                    "single", "rmbg", "interrogate", "reactor_image"))

DrawTaskStatus = Enum("DrawTaskStatus", ("New", "Fetched",
                      "Drawing", "Succ", "Failed"))


handlers = {}


def zy_route(task_type):
    def draw_func(func):
        global handlers

        @wraps(func)
        def wraper(*args, **kwargs):
            return func(*args, **kwargs)

        handlers[task_type] = wraper
        return wraper

    return draw_func


def handle_task(api, client, task_id, task_type, params, owner):

    logger = get_logger()
    handle = handlers.get(task_type, None)
    if handle == None:
        logger.info(f"hanle wrong task type:{task_type}")
        return

    handle(api, client, task_id, params, owner)


@zy_route(DrawTaskType.txt2img.value)
def do_txt2img(api, client: DrawClient, task_id, params: dict, owner):
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
        imgs = batch_watermark(images[:pic_number], owner)
        succ, image_info = upload_to_oss(imgs)

    status = DrawTaskStatus.Failed
    if succ:
        status = DrawTaskStatus.Succ

    client.update_status(task_id,  status, {
        "images": image_info,
        "draw_type": "txt2img",
        "gen_meta": gen
    })

    logger.info(f"Update status to backend: {image_info}")


@zy_route(DrawTaskType.img2img.value)
def do_img2img(api, client: DrawClient, task_id, params: dict, owner):
    from modules.api.api import Api
    from modules.api.models import StableDiffusionImg2ImgProcessingAPI

    A: Api = api
    logger = get_logger()
    req = StableDiffusionImg2ImgProcessingAPI()
    params.pop("model_id")
    params.pop("mode")
    real_req = req.copy(update=params)
    images, gen, pic_number = api.img2img(real_req)

    image_info = []
    succ = False
    if len(images) != 0:
        imgs = batch_watermark(images[:pic_number], owner)
        succ, image_info = upload_to_oss(imgs)

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
def do_single(api, client: DrawClient, task_id, params: dict, owner):
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
        imgs = batch_watermark(images, owner)
        succ, image_info = upload_to_oss(imgs)

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
def do_rmbg(api, client: DrawClient, task_id, params: dict, owner):
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
        imgs = batch_watermark(images, owner)
        succ, image_info = upload_to_oss(imgs)

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

    from extensions.sdwebuiwd14tagger.tagger.api import get_api, models, on_app_started
    logger = get_logger()

    file = params.get("file", {})
    image = get_image_from_oss(
        task_id, file["path"], bucket_name=file["bucket"])

    req = fakeReq()
    req.image = image
    req.model = params.get("model")
    req.threshold = params.get("threshold", 0.35)

    A = get_api()
    if A == None:
        on_app_started(None, api)
        A = get_api()

    rsp = A.endpoint_interrogate(req)

    client.update_status(task_id, DrawTaskStatus.Succ, {
        "result": rsp.caption
    })


@zy_route(DrawTaskType.reactor_image.value)
def do_reactor_image(api, client: DrawClient, task_id, params: dict):

    from extensions.sdwebuireactor.scripts.reactor_api import reactor_image
    logger = get_logger()

    source_image_url = params.get("source_image", "")
    source_image = get_image_from_oss(f"{task_id}_1", source_image_url[35:], bucket_name="zy-puzzle")
    source_image_buf = BytesIO()
    source_image.save(source_image_buf, format='PNG')

    target_image_url = params.get("target_image", "")
    target_image = get_image_from_oss(f"{task_id}_2", target_image_url[35:], bucket_name="zy-puzzle")
    target_image_buf = BytesIO()
    target_image.save(target_image_buf, format='PNG')

    req = {
        "mask_face": 1,
        "face_restorer": "CodeFormer",
        "target_image": base64.b64encode(target_image_buf.getvalue()),
        "source_image": base64.b64encode(source_image_buf.getvalue())
    }
    rsp = reactor_image(**req)
    image = upload_to_puzzle(pic_id=params.get("pic_id"), image=base64.b64decode(rsp.get("image")))

    client.update_status(task_id, DrawTaskStatus.Succ, {
        "image": image
    })
