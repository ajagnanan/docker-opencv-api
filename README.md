# OpenCV Webservices

### Build Instructions

To build the project, execute the following command in the project root:

```
docker build -t opencv-api .
```

### Run Instructions

To run the project, execute the following command in the project root:

```
docker run -d -p 8888:8888 opencv-api
```

or run with docker-compose:

```
docker-compose up -d
```

#### Options

Options can be controlled with environment variables:

```
OCV_COUNTRY_CODE=us
OCV_TOP_N=5
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

