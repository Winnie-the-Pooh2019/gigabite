FROM python:3.12-alpine


WORKDIR /app
VOLUME /app/prompt

COPY ./main.py .
COPY ./requirements.txt .
COPY ./.env .

RUN python3 -m venv /app/.venv
RUN source /app/.venv/bin/activate
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python3", "./main.py"]