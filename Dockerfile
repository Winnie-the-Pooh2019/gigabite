FROM python:3.12-alpine


WORKDIR /app

COPY . .

#RUN apt install python3.12-venv
RUN python3 -m venv /app/.venv
RUN source /app/.venv/bin/activate
RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python3", "./main.py"]