FROM python:2.7

RUN  \
  apt-get update \
  && apt-get -y install vim python-virtualenv libxml2-dev libxslt-dev python-pip python-dev

ADD data.tar /
ADD nltk_data.tar /usr/share/
ADD att.tar /

RUN \
 cd att && \
 . venv/bin/activate && \
 python setup.py install 

VOLUME /output 

ADD conf.tar /
ADD align.sh /

ENTRYPOINT [ "/bin/bash", "/align.sh" ]

