import os
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    author = event.data["issue"]["user"]["login"]
    message = f"Howdy {author} Thanks for creating an issue!"
    url = event.data["issue"]["comments_url"]
    await gh.post(url, data={"body": message})


@router.register("pull_request", action="closed")
async def issue_pr_thanks_you(event, gh, *args, **kwargs):
    merged = event.data["pull_request"]["merged"]
    if merged is True:
        url = event.data["pull_request"]["comments_url"]
        author = event.data["pull_request"]["user"]["login"]
        message = f"Howdy {author}! Thanks for contributing"
        await gh.post(url, data={"body": message})


@router.register("issue_comment", action="created")
async def thumbs_up_my_comments(event, gh, *args, **kwargs):
    comment_url = event.data["issue_comment"]["comment"]["url"]
    author = event.data["issue_comment"]["comment"]["user"]["login"]

    if author == "annielcook":
        await gh.post(f"{comment_url}/reactions", data={
            "content": "heart"
        })


async def main(request):
    # read the GitHub webhook payload
    body = await request.read()

    # our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of GitHub webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # instead of mariatta, use your own username
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "annielcook",
                                  oauth_token=oauth_token)

        # call the appropriate callback for the event
        await router.dispatch(event, gh)

    # return a "Success"
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
