# OpenALPR Webservice

### Build Instructions

To build the project, execute the following command in the project root:

```
docker build -t openalpr-web .
```

### Run Instructions

To run the project, execute the following command in the project root:

```
docker run -d -p 8888:8888 openalpr-web
```

or run with docker-compose:

```
docker-compose up -d
```

#### Options

Options can be controlled with environment variables:

```
ALPR_COUNTRY_CODE=us
ALPR_TOP_N=5
```

### Available APIs

License plate recognition

```
POST /alpr
```

e.g.
```
curl -X POST -F "image=@assets/license_fl.jpg" http://localhost:8888/alpr
```

___
QR code recognition

```
POST /qr
```

e.g.
```
curl -X POST -F "image=@assets/qr_1.jpg" http://localhost:8888/qr
```

