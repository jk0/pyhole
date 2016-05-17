#!/bin/bash

#   Copyright 2016 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

set -x

clear

git pull origin master

docker build -t pyhole .
docker stop pyhole
docker rm pyhole
docker run -d -p 80:5000 -v /mnt/pyhole:/root/.pyhole -v /etc/hosts:/etc/hosts:ro --name pyhole pyhole
docker ps
docker logs -f pyhole
