FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY src ./src
COPY ./src /code/src


CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]


# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]