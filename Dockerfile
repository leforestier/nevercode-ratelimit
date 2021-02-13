FROM python:3.6-alpine
RUN pip install --upgrade pip
RUN adduser -D worker
USER worker
RUN mkdir /home/worker/src
ENV PYTHONPATH="/home/worker/src:${PATH}"
ENV PATH="/home/worker/.local/bin:${PATH}"
RUN pip install Flask docopt --user
COPY --chown=worker:worker ratelimit /home/worker/src/ratelimit
COPY --chown=worker:worker demoapp /home/worker/src/demoapp
WORKDIR /home/worker/src/
EXPOSE 5000
ENTRYPOINT ["python", "-m", "demoapp"]
