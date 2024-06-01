FROM debian:bookworm

RUN apt-get -y update && apt-get install -y python3 python3-pip python3-venv python3-dev pkg-config libcairo2-dev ffmpeg libsm6 libxext6 libx11-6 libxcb1 libxau6 libgl1-mesa-dev xvfb dbus-x11 x11-utils libxkbcommon-x11-0 libavcodec-dev libavformat-dev libswscale-dev && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

WORKDIR /root/workdir/

COPY . .

RUN chmod u+x *.sh

RUN bash -c "source /opt/venv/bin/activate && ./student_install.sh"
RUN bash -c "source /opt/venv/bin/activate && ./dev_requirements.sh"

RUN echo '#!/bin/bash\nsource /opt/venv/bin/activate\nxvfb-run --server-args "-ac -screen 0, 1024x1024x24" ./run.sh adv_symmetry/configs/*.json' > /root/workdir/entrypoint.bash && chmod u+x /root/workdir/entrypoint.bash

ENTRYPOINT [ "/root/workdir/entrypoint.bash" ]
