#!/usr/local/bin/python3

"""Authors: Bartek Kryza
Copyright (C) 2022 Onedata
This software is released under the MIT license cited in 'LICENSE'
"""

import json
import sys
import os
import sys
import httpx
from datetime import datetime
from decorest import *


if len(sys.argv) != 5:
    print("Usage:\nmain.py <PROVIDER_HOST> <SPACE_ID> <OUTPUT_DIR> <ACCESS_TOKEN>")
    sys.exit(1)


PROVIDER_HOST = sys.argv[1]
SPACE_ID = sys.argv[2]
OUTPUT_DIR = sys.argv[3]
ACCESS_TOKEN = sys.argv[4]
PAGE_SIZE = 1000


@backend('httpx')
@endpoint(f'https://{PROVIDER_HOST}/api/v3/oneprovider')
@header('X-Auth-Token', ACCESS_TOKEN)
class OneproviderClient(RestClient):

    @GET('data/{parent_id}/files')
    @accept('application/json')
    @query('token')
    @query('limit')
    @timeout(120)
    def list_files(self, parent_id, token, limit=PAGE_SIZE):
        """List files"""


def generate_file_path():
    dt_format = '%y%m%d%H%M%S'
    return os.path.join(OUTPUT_DIR, f'backup_{SPACE_ID}_{datetime.now().strftime(dt_format)}.json')

RETRY_COUNT_MAX = 5

if __name__ == '__main__':
    op_client = OneproviderClient()
    is_last = False
    backup_file_path = generate_file_path()
    status = 0
    page_count = 0
    with open(backup_file_path, 'w') as f:
        with op_client.session_(verify=False) as s:
            print(f'Starting backup of space {SPACE_ID} to file {backup_file_path}...')
            next_page_token = ""

            f.write("[\n")

            retry_count = RETRY_COUNT_MAX
            while not is_last:
                try:
                    res = s.list_files(SPACE_ID, next_page_token)
                    retry_count = RETRY_COUNT_MAX
                except HTTPErrorWrapper as e:
                    if isinstance(e.wrapped, httpx.TimeoutException):
                        retry_count -= 1
                        if retry_count == 0:
                            print("Maximum timeout retry exceeded - aborting...")
                            status = 1
                            break
                        print(f"Retrying due to error: {e}")
                        continue
                    else:
                        print(f"{e.response.text}")
                        status = 1
                        break

                is_last = res['isLast']

                if 'files' in res:
                    i = len(res['files']) - 1
                    for file in res['files']:
                        if is_last and i == 0:
                            f.write(f'{json.dumps(file)}\n')
                        else:
                            f.write(f'{json.dumps(file)},\n')
                        i -= 1

                f.flush()

                next_page_token = res['nextPageToken'] if 'nextPageToken' in res else None

                page_count += 1
                if page_count % 10  == 0:
                    print(f'  saved {PAGE_SIZE*page_count} paths')

            f.write("]\n")

    if status != 0:
        print(f"ERROR: Backup failed after {page_count*1000} items")
        sys.exit(status)

    print(f'Compressing backup file to {backup_file_path}.zst')

    os.system(f'zstd -z {backup_file_path}')

    print(f'Removing uncompressed backup file {backup_file_path}')

    os.system(f'rm -f {backup_file_path}')

    print(f'Backup completed')
