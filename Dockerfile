# Docker file to run Hashicorp Vault (vaultproject.io)
FROM drunner/baseimage-alpine
MAINTAINER drunner

RUN apk add --update bash python py-pip build-base python-dev py-boto py-mysqldb && rm -rf /var/cache/apk/*
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
VOLUME /config /resources
