# OpenCV Webservices

## Build Instructions

To build the project, execute the following command in the project root:

```
docker build -t docker-opencv-api .
```

---
Please reference the [mxnet model gallery](https://github.com/dmlc/mxnet-model-gallery) for accuracy details.

## Run Instructions

To run the project, use docker-compose for quick configuration setup:

```
docker-compose up -d
```

#### Options

Options can be controlled with environment variables:

```
OCV_COUNTRY_CODE=us
OCV_TOP_N=5
OCV_MXNET_MODEL=squeezenet_v1.1 || vgg19
```

## Available APIs

Healthcheck

```
GET /health
```

e.g.
```
curl -X GET http://localhost:8888/health
```

---
License plate recognition

```
POST /lpr
```

e.g.
```
curl -X POST -F "image=@assets/lpr_1.jpg" http://localhost:8888/lpr
```

___
QR code recognition

```
POST /qrr
```

e.g.
```
curl -X POST -F "image=@assets/qrr_1.jpg" http://localhost:8888/qrr
```

___
OpenFace recognition

```
POST /ofr
```

e.g.
```
curl -X POST -F "image=@assets/ofr_1.jpg" http://localhost:8888/ofr
```

___
Object detection recognition

```
POST /odr
```

e.g.
```
curl -X POST -F "image=@assets/odr_1.jpg" http://localhost:8888/odr
```

___
Build OpenFace model

```
POST /faces/generate
```

e.g.
```
curl -X POST http://localhost:8888/faces/generate
```

Generating the model requires that images be in the `openface` folder, which is mounted into the docker container under `/root/data`. Additional metadata can be added to the `openface/data.json` file with the key being the folder names in the `openface/images` folder. The model is generated and stored in `openface/data.pickle`. This file can be included statically into an extension image so that generating it isn't necessary.

An "unknown" dataset is included along with the trained data.pickle to detect unknown faces following the recommendation of [issue #144](https://github.com/cmusatyalab/openface/issues/144)
___
Faces site

```
GET /faces
```

e.g.
```
http://localhost:8888/faces
```

___
Faces by uid

```
POST /faces/:uid
```

e.g.
```
http://localhost:8888/faces/dwayne
```

##### Deployment

[Openshift Online v3](https://manage.openshift.com/) allows for easy `docker-compose.yml` deployments. After configuring the CLI tool, execute the following command to import it into Openshift:

```
oc import docker-compose -f docker-compose.yml
```

and configure a route after the pod is up.

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Additionally, the following projects were used as a guideline and their license should be followed as well:

- [https://github.com/ankushagarwal/openalpr-web](https://github.com/ankushagarwal/openalpr-web)
- [https://github.com/Maitm29/QR-code](https://github.com/Maitm29/QR-code)
- [https://github.com/UoA-eResearch/openface_mass_compare](https://github.com/UoA-eResearch/openface_mass_compare)