import os
import random
import string
import asyncio
from subprocess import run, DEVNULL
from typing import Literal, get_args


LANGUAGES = Literal["python", "rickroll-lang", "node"]  # supported languages


async def cleanup(random_code: str) -> None:
    """
    Cleans up the docker stuff

    Parameters
    ----------
        random_code (str): The random generated name (image name)

    Deletes the image that was made
    Also if it has made a container it will kill and delete that container too
    """
    await asyncio.sleep(5)

    image = run(
        ["docker", "images", "-q", random_code], capture_output=True
    ).stdout.decode()
    container = run(
        ["docker", "ps", "-a", "-q", "--filter", f"ancestor={image}"],
        capture_output=True,
    ).stdout.decode()

    # >/dev/null 2>&1 just makes it so it does not print the output of the command to terminal
    os.system(f"docker container kill {container} >/dev/null 2>&1")
    os.system(f"docker container rm -f {container} >/dev/null 2>&1")
    os.system(f"docker image rm -f {image} >/dev/null 2>&1")


async def run_code(code: str, language: LANGUAGES, **kwargs) -> str:
    """
    Runs the code given in a language

    Parameters
    ----------
        code (str): The code
        language (str): The language you want to run in. See `LANGUAGES`

        Keyword Arguments:
            await_task (bool): This creates an asyncio task in the event loop to cleanup the docker mess.
                You need to be in an event loop to use this because if not it will kill the task before it starts
                Turning this on will make the output be returned faster

    Returns
    -------
        str : The output of the code runned

    """

    if language not in list(get_args(LANGUAGES)):  # Check if language is in the list of languages
        return f"Not a valid lanuage\nList: {', '.join(list(get_args(LANGUAGES)))}"

    random_code_list = (string.ascii_lowercase + string.digits)  # create a random name for the docker image
    random_code = "".join([random.choice(random_code_list) for i in range(12)])

    code = repr(code).strip("'")  # idk why this works but it does

    run([
        "docker", "build", 
        "-t", random_code, f"./{language}/",
        "--build-arg", f"CODE={code}",
    ], stdout=DEVNULL,stderr=DEVNULL,)  # build the container

    output = run([
            "timeout", "-s", "KILL", "3",
            "docker","run",
            "--rm",
            "--read-only",
            "--network", "none",
            random_code,
        ], capture_output=True, ).stdout.decode()  # run the container

    if len(output) > 4000:  # if the output is more than 4000 characters it will crop it to 4000 characters
        output = output[:4000]

    if "await_task" in kwargs and kwargs["await_task"]:  # checks if this is true
        loop = asyncio.get_event_loop()
        loop.create_task(cleanup(random_code))  # cleanup
    else:
        await cleanup(random_code)  # cleanup

    return output