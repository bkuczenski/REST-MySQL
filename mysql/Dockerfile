FROM python:3.8
RUN mkdir /usr/src/mysql/
COPY . /usr/src/mysql/
WORKDIR /usr/src/mysql/
RUN pip install -r requirements.txt
CMD ["python", "add_admin.py"]