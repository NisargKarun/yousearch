FROM python:3.9
COPY ./ /app
RUN cd /app && pip install -r requirements.txt
WORKDIR /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]