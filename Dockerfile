FROM ubuntu:20.04

ARG VERSION=1.6.5

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends python3-pip python3.9-dev libopenal-dev libsdl2-dev libvorbis-dev cmake clang-format wget

WORKDIR /app

# RUN wget -O bombsquad.tar.gz https://files.ballistica.net/bombsquad/builds/BombSquad_Server_Linux_${VERSION}.tar.gz && \
#     tar -xvf bombsquad.tar.gz && \
#     mv BombSquad_Server_Linux_${VERSION} bombsquad-server && \
#     rm -f bombsquad.tar.gz && \
#     awk '/transition_delay=self._min_view_time).autoretain()/ { print; print "        import mystats\n        mystats.update(self._stats)"; next }1' /app/bombsquad-server/dist/ba_data/python/ba/_activitytypes.py > /tmp/_activitytypes.py && \
#     mv /tmp/_activitytypes.py /app/bombsquad-server/dist/ba_data/python/ba/_activitytypes.py && \
#     mkdir -p /app/bombsquad-server/dist/ba_root/mods/
#
# ADD *.py /app/bombsquad-server/dist/ba_root/mods/

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/*

ADD . /app/bombsquad-server

WORKDIR /app/bombsquad-server

EXPOSE 43210/udp

CMD ["/app/bombsquad-server/bombsquad_server"]
