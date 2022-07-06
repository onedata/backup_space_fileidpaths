#  backup_space_fileidpaths

Backup script for downloading filepath to storage file id mappings from Onedata spaces.


## Usage

```bash
main.py <PROVIDER_HOST> <SPACE_ID> <OUTPUT_DIR> <ACCESS_TOKEN>
```

for example

```bash
main.py demo.onedata.org 8031e7b1c614d92dc57d5bb239d68843ch14d9 /mnt/backups/onedata FAe41dba930e76e89df0c21c6392bbe7133ch6e89dba930e76e89df0c21c6392b
```

## Docker
To build and use the Docker image from this repository:

```bash
docker build -t backup_space_fileidpaths .
docker run -v /mnt/backups/onedata:/mnt/backups/onedata backup_space_fileidpaths demo.onedata.org 8031e7b1c614d92dc57d5bb239d68843ch14d9 /mnt/backups/onedata FAe41dba930e76e89df0c21c6392bbe7133ch6e89dba930e76e89df0c21c6392b
```
