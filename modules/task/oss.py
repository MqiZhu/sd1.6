# coding=utf-8
from PIL import Image
import oss2
from io import BytesIO
from snowflake import SnowflakeGenerator


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
        oss_name = f"{gen_aigc_oss_id()}.png"

        with BytesIO() as buf:
            image.save(buf, 'png')
            img_data = buf.getvalue()
            bucket_name = "magic-wand-sd"
            upload_to_google_oss(bucket_name, img_data, oss_name)
            images.append({
                "url": f"https://storage.googleapis.com/magic-wand-sd/{oss_name}",
                "bucket": bucket_name,
                "size": len(img_data)
            })
        # result = bucket.put_object(oss_name, img_data)
        # buf.close()
            
    return len(images_gen) == len(images), images


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
    return f"https://cdn-puzzle.magicwand.so/tmp/{pic_id}.png"


from google.cloud import storage
from google.oauth2 import service_account


def upload_to_google_oss(bucket_name, source_file, destination_blob_name):
    """Uploads a file to the bucket."""
    # The path to your service account key file
    key_path = "/data/service-account-gcs.json"

    # Explicitly use service account credentials by specifying the private key file.
    credentials = service_account.Credentials.from_service_account_file(key_path)

    # Initialize the Google Cloud Storage client with your credentials
    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob (file) in the bucket and upload the file's content
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(source_file)

    print(f"Google Cloud Storage: file uploaded to {destination_blob_name}.")
