#!/usr/local/bin/python3

import json
import sys
import os
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
    def list_files(self, parent_id, token, limit=PAGE_SIZE):
        """List files"""


def generate_file_path():
    dt_format = '%y%m%d%H%M%S'
    return os.path.join(OUTPUT_DIR, f'backup_{SPACE_ID}_{datetime.now().strftime(dt_format)}.json')


if __name__ == '__main__':
    op_client = OneproviderClient()
    is_last = False
    backup_file_path = generate_file_path()
    with open(backup_file_path, 'w') as f:
        with op_client.session_(verify=False) as s:
            print(f'Starting backup of space {SPACE_ID} to file {backup_file_path}...')
            next_page_token = ""

            f.write("[\n")

            page_count = 0
            while not is_last:
                res = s.list_files(SPACE_ID, next_page_token)

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

    print(f'Compressing backup file to {backup_file_path}.zst')

    os.system(f'zstd -z {backup_file_path}')

    print(f'Removing uncompressed backup file {backup_file_path}')

    os.system(f'rm -f {backup_file_path}')

    print(f'Backup completed')
