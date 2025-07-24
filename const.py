import os
DEBUG_MODE = os.path.exists(".debug")

BCRYPT_SALT_ROUNDS = 14

TOKEN_EXPIRY_TIME = 30 * 24 * 60 * 60 # 30 days in seconds

POSTS_PER_PAGE = 10

UPLOAD_FOLDER = "post_media"

MAX_TITLE_LENGTH = 10