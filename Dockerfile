# This docker image provides an environment where prh is installed from local source via pip
# and is therefore suitable for non-MacOS/non-Homebrew environments (eg. CI workflows)

FROM doximity/ruby2.4-python-browsers

ADD . /prh_source

RUN cd /prh_source && mkdir -p /opt/prh && sed -i 's/config_file_path/\/opt\/prh/' prhpackage/__main__.py && pip install .
