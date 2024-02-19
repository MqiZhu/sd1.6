# coding=utf-8
from PIL import Image
import oss2
from io import BytesIO
from snowflake import SnowflakeGenerator
import requests
import json

auth = oss2.Auth("LTAI5tQnLUQgZSY9xy7rz2fL", "eIVPKw6R7eSv2Mt2EJ6ZJJ9Rh3HKqJ")

default_bucket_name = 'zy-pic-items-test'
bucket = oss2.Bucket(
    auth, 'oss-cn-hangzhou.aliyuncs.com/', default_bucket_name)

tmp_bucket_name = 'drawtask-tmp'
bucket_tmp = oss2.Bucket(
    auth, 'oss-cn-hangzhou.aliyuncs.com/', tmp_bucket_name)


puzzle_bucket_name = 'zy-puzzle'
bucket_puzzle = oss2.Bucket(
    auth, 'oss-cn-hangzhou.aliyuncs.com/', puzzle_bucket_name)

aigc_id_gen = SnowflakeGenerator(1023)
REMEMBER_COOKIE_NAME = 'greatleapai_token'


def gen_aigc_oss_id():
    val = next(aigc_id_gen)
    return val


def upload_to_oss(images_gen) -> bool:

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
            "bucket": "zy-pic-items-test",
            "size": len(img_data)
        })

    return True, images


def get_image_from_oss(task_id, path, bucket_name=default_bucket_name):

    user_bucket = bucket
    if bucket_name == tmp_bucket_name:
        user_bucket = bucket_tmp
    elif bucket_name == puzzle_bucket_name:
        user_bucket = bucket_puzzle

    file_name = f"/tmp/{task_id}.png"
    obj = user_bucket.get_object_to_file(path, file_name)
    image = Image.open(file_name)

    return image


def upload_to_puzzle(pic_id, image):
    key = f"tmp/{pic_id}.png" 
    bucket_puzzle.put_object(key, image)
    return f"https://cdn.greatleapai.com/tmp/{pic_id}.png"
