#!/bin/bash

curl -s https://raw.githubusercontent.com/MeSmallMan/logo/main/logo0.sh | bash


docker stop elixir && docker rm elixir
docker pull elixirprotocol/validator:v3
docker run -d --env-file /root/validator.env --name elixir --restart unless-stopped -p 17690:17690 elixirprotocol/validator:v3

echo "Thanks <3"
