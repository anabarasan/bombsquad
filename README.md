# Stats Mod for BombSquad

updated for v1.6.5

## publishing the stats

- copy the index.html to your webserver
- change mysettings.stats_file path such that the stats.json file is adjacent to index.html

## Docker commands

build docker image

```
docker build -t bombsquad:1.6.5  .
```

running the server via docker

```
docker run --rm -it -p 43210:43210/udp -e BA_ACCESS_CHECK_VERBOSE=1 -v /var/www/html:/var/www/html --name bombsquad bombsquad:1.6.5
```

logging into the container to check the files

```
docker exec -it bombsquad bash
```
