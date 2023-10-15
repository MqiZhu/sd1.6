# coding=utf-8
from PIL import Image
import oss2
from io import BytesIO
import fastapi
from snowflake import SnowflakeGenerator
from modules.processing import StableDiffusionProcessingTxt2Img, StableDiffusionProcessingImg2Img, StableDiffusionProcessing

import gradio as gr
import requests
import json

auth = oss2.Auth("LTAI5tQnLUQgZSY9xy7rz2fL", "eIVPKw6R7eSv2Mt2EJ6ZJJ9Rh3HKqJ")
bucket = oss2.Bucket(
    auth, 'oss-cn-hangzhou.aliyuncs.com/', 'zy-pic-items-test')

zy_backend_host = "https://api-zy.greatleapai.com"
zy_backend_url = "{}/items/create_txt2img_sd".format(zy_backend_host)
zy_backend_subcoin_url = "{}/items/create_subcoin".format(zy_backend_host)
zy_backend_trans_url = "{}/trans/chtoen".format(zy_backend_host)


aigc_id_gen = SnowflakeGenerator(1023)
REMEMBER_COOKIE_NAME = 'greatleapai_token'


def gen_aigc_oss_id():
    val = next(aigc_id_gen)
    return val


def call_zy_backend(conn: gr.Request, url, data):
    headers = {
        "cookie": conn.headers.cookie
    }
    rsp = requests.post(url, json=data, headers=headers)

    return rsp.status_code, rsp.text

def call_zy_backend_with_fastapi(req: fastapi.Request, url, data):
    headers = {
        "cookie": req.headers.get("cookie")
    }
    rsp = requests.post(url, json=data, headers=headers)

    return rsp.status_code, rsp.text



def translate_promt(req:fastapi.Request, prompt, ne_prompt):
    data = {"promt": prompt, "ne_promt": ne_prompt}

    code, result = call_zy_backend_with_fastapi(req, zy_backend_trans_url, data);
    if code != 200:
        print("failed", code, result)
        return False, '', ''

    print(code, result)
    rsp = json.loads(result)
    res_code = rsp.get("status_code", 0)
    if res_code != 200:
        return False, '', ''

    ret_data = rsp.get("data", {})

    return True, ret_data["promt"], ret_data["ne_promt"]


def create_aigc_item_subcoin(conn: gr.Request, draw_type, model_name, input_data):
    data = {
        "model_name": model_name,
        "input_data": input_data,
        "dray_type": draw_type,
    }

    status_code, rsp_text = call_zy_backend(conn, zy_backend_subcoin_url, data)
    print(status_code, rsp_text)
    if status_code != 200:
        return False, 0

    rsp = json.loads(rsp_text)
    data = rsp.get("data", {})

    if data == None or data.get("coin", 0) == 0:
        return False, 0

    return True, data["coin"]


def create_aigc_item_api(req: fastapi.Request, draw_type, model_name, input_data, images_gen, gen_info) -> bool:

    images = []

    for image in images_gen:
        id = gen_aigc_oss_id()
        oss_name = "{}.png".format(id)

        buf = BytesIO()
        image.save(buf, 'png')

        img_data = buf.getvalue()
        result = bucket.put_object(oss_name, img_data)
        buf.close()

        images.append({
            "url": "https://cdn.greatleapai.com/{}".format(oss_name),
            "size": len(img_data)
        })

    data = {
        "gen_meta": json.loads(gen_info),
        "draw_type": draw_type,
        "model_name": model_name,
        "input_data":  input_data,
        "images": images,
    }

    status_code, rsp_text = call_zy_backend_with_fastapi(req, zy_backend_url, data)
    print("request rsp: ", status_code, rsp_text)

    if status_code != 200:
        return False, []

    rsp_obj = json.loads(rsp_text)
    #"data":{"image_ids":[7101215495067541504]
    image_ids = rsp_obj.get("data", {}).get("image_ids")
    image_info = []

    for i, img in enumerate(images):
        image_info.append({
            "url": img["url"],
            "item_id": str(image_ids[i]),
        })
    
    return True, image_info

def create_aigc_item(conn: gr.Request, draw_type, model_name, input_data, images_gen, gen_info) -> bool:

    images = []
    if len(images_gen) > 1:  # 第一张是混合的缩略图，处理下
        images_gen = images_gen[1:]

    for image in images_gen:
        id = gen_aigc_oss_id()
        oss_name = "{}.png".format(id)

        buf = BytesIO()
        image.save(buf, 'png')

        img_data = buf.getvalue()
        result = bucket.put_object(oss_name, img_data)
        buf.close()

        images.append({
            "url": "https://cdn.greatleapai.com/{}".format(oss_name),
            "size": len(img_data)
        })

    data = {
        "gen_meta": json.loads(gen_info),
        "draw_type": draw_type,
        "model_name": model_name,
        "input_data":  input_data,
        "images": images,
    }

    status_code, rsp_text = call_zy_backend(conn, zy_backend_url, data)
    print("request rsp: ", status_code, rsp_text)

    if status_code != 200:
        return False
    return True

def create_from_processing(req:fastapi.Request, p: StableDiffusionProcessing, item_type, model_name, vae_name, images, generation_info_js):

    input_data = {
            "prompt": p.prompt,
            "styles": p.styles,
            "negative_prompt": p.negative_prompt,
            "seed": p.seed,
            "subseed": p.subseed,
            "subseed_strength": p.subseed_strength,
            "seed_resize_from_h": p.seed_resize_from_h,
            "seed_resize_from_w": p.seed_resize_from_w,
            "sampler_index": p.sampler_index,
            "sampler_name": p.sampler_name,
            "batch_size": p.batch_size,
            "n_iter": p.n_iter,
            "steps": p.steps,
            "cfg_scale": p.cfg_scale,
            "width": p.width,
            "height": p.height,
            "restore_faces": p.restore_faces,
            "tiling": p.tiling,
            "denoising_strength": p.denoising_strength,
            "override_settings": p.override_settings,
            "vae":vae_name,
    }

    images = images[:p.batch_size]
    succ, urls = create_aigc_item_api(req, item_type, model_name, input_data,
                            images, generation_info_js)

    return succ, urls
