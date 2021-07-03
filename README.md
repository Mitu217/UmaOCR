# UMA OCR

OCR to get information from ウマ娘's UI image

# Future

- [x] Get status from StatusModal ScreenShot

# Usage

1. run docker container
```shell
$ docker-compose up -d
```

1. open browser to `http://localhost:8080` or run command below

```shell
$ curl -X POST http://localhost:8080/api/v1/ocr/status -F file=@{FILE_PATH}
```
