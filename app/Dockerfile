FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
WORKDIR /usr/src/app/
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /usr/src/app/requirements.txt
COPY . /usr/src/app/
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]