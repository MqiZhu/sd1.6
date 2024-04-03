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
        oss_name = f"items/{gen_aigc_oss_id()}.png"

        with BytesIO() as buf:
            image.save(buf, 'png')
            img_data = buf.getvalue()
            bucket_name = "magic-wand-sd"
            upload_to_google_oss(bucket_name, img_data, oss_name)
            images.append({
                "url": f"https://www.magicwand.so/magic-wand-sd/{oss_name}",
                "bucket": bucket_name,
                "size": len(img_data)
            })
        # result = bucket.put_object(oss_name, img_data)
        # buf.close()
            
    return len(images_gen) == len(images), images

def upload_to_tmp_oss(images_gen) -> bool:
    print(f"images_gen: {images_gen}")
    images = []

    for image in images_gen:
        oss_name = f"tmp/{gen_aigc_oss_id()}.png"

        with BytesIO() as buf:
            image.save(buf, 'png')
            img_data = buf.getvalue()
            bucket_name = "magic-wand-sd"
            upload_to_google_oss(bucket_name, img_data, oss_name)
            images.append({
                "url": f"https://www.magicwand.so/magic-wand-sd/{oss_name}",
                "bucket": bucket_name,
                "size": len(img_data)
            })
        # result = bucket.put_object(oss_name, img_data)
        # buf.close())


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

def get_image_from_tmp_oss(path):
    return Image.open(download_to_google_oss(path))


def upload_to_puzzle(pic_id, image):
    key = f"tmp/{pic_id}.png" 
    bucket_puzzle.put_object(key, image)
    return f"https://cdn-puzzle.magicwand.so/tmp/{pic_id}.png"


from google.cloud import storage
from google.oauth2 import service_account


def upload_to_google_oss(bucket_name, source_file, blob_name):
    """Uploads a file to the bucket."""
    # The path to your service account key file
    key_path = "/home/puncsky/service-account-gcs.json"

    # Explicitly use service account credentials by specifying the private key file.
    credentials = service_account.Credentials.from_service_account_file(key_path)

    # Initialize the Google Cloud Storage client with your credentials
    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob (file) in the bucket and upload the file's content
    blob = bucket.blob(blob_name)
    blob.upload_from_string(source_file)

    print(f"Google Cloud Storage: Uploaded to {blob_name} to bucket {bucket_name}.")


def download_to_google_oss(bucket_name, blob_name) -> bytes:
    """Uploads a file to the bucket."""
    # The path to your service account key file
    key_path = "/home/puncsky/service-account-gcs.json"

    # Explicitly use service account credentials by specifying the private key file.
    credentials = service_account.Credentials.from_service_account_file(key_path)

    # Initialize the Google Cloud Storage client with your credentials
    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()
    print(f"Google Cloud Storage: Downloaded storage object {blob_name} from bucket {bucket_name}.")
    return contents
