FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl
EXPOSE 8080
CMD ["apache2ctl", "-D", "FOREGROUND"]
