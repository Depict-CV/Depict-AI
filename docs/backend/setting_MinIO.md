to simulate s3 bucket ( or any cloud stoareg solution)
I use MinIO so each data will be accesible via an url


to launch the docker here is the command:

docker run -p 9000:9000 -p 9001:9001 -e "MINIO_ROOT_USER=admin" -e "MINIO_ROOT_PASSWORD=admin123" quay.io/minio/minio server /data --console-address ":9001"