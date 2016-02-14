# Docker file to run Hashicorp Vault (vaultproject.io)
FROM drunner/baseimage-alpine
MAINTAINER drunner

# we use non-root user in the container for security.
# dr expects uid 22022 and gid 22022.
   # - debian
   #RUN groupadd -g 22022 drgroup
   #RUN adduser --disabled-password --gecos '' -u 22022 --gid 22022 druser
# - alpine
RUN apk add --update bash python py-pip build-base python-dev py-boto && rm -rf /var/cache/apk/*
RUN pip install --upgrade pip
RUN pip install awscli ansible

# add in the assets.
COPY ["./drunner","/drunner"]
COPY ["./ansible","/ansible"]
COPY ["./usrlocalbin","/usr/local/bin/"]
RUN chmod a+rx -R /usr/local/bin  &&  \
    chmod a-w -R /drunner  &&  \
    chmod a-w -R /ansible  &&  \
    chmod a-x -R /ansible/*

# lock in druser.
USER druser

# expose volume
VOLUME /config
