#!/bin/bash
podman run --rm -it --net host -v ./prometheus.yml:/etc/prometheus/prometheus.yml:z prom/prometheus
