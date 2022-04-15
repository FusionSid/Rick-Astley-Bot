FROM fusionsid/ricklang

ARG CODE

RUN echo -e ${CODE} > code.rickroll

CMD ["timeout", "-s", "KILL", "5", "python3", "RickRoll.py", "code.rickroll"]