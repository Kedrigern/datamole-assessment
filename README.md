# Datamole assessment

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0055FF?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![uv](https://img.shields.io/badge/built%20with-uv-blueviolet)](https://astral.sh/blog/uv)

## Prepare

[uv](https://docs.astral.sh/uv/) is used to manage python.

```bash
cp .env.example .env
gh auth token   # obtain access token
vim .env        # write your values
uv sync         # install python packages
uv run pytest   # run the tests
```

## Run

```bash
uv run fastapi dev src/app.py
```

This command starts the FastAPI development server using uv. The dev flag enables hot reloading, so the server will automatically restart when you make changes to the code.

Once the server is running, you can access the application in your web browser at `http://127.0.0.1:8000`.

There are few **endpoints**:

`/`: Returns basic information about the application. This is a good way to check if the server is running.

`/docs`: Provides access to the interactive **Swagger UI** documentation.

`/fetch`: Fetch data from gh API to local DB

`/fetch/{org}/{repo}`: Fetches event data specifically for the given repository within the specified organization from the GitHub API and stores it in the local database.

`/stats/{org}/{repo}/{event_type}`: Calculates and returns the average time difference (in seconds) between consecutive events of the specified `event_type` within the given repository. The calculation is based on the rolling window logic (7 days or 500 events).

## Architecture

This demo application is designed to calculate statistics from the [GitHub Events API](https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28). The goal:

> It generates statistics based on a rolling window of either 7 days or 500 events, whichever is less. These statistics are made available to end-users via a REST API. Specifically, the API will show the average time between consecutive events, separately for each combination of event type and repository name.

Application use local DB (SQLite). When you call `/fetch` application download
events from API and parse part of info into local DB. The calls to the api are cached with [Requests-Cache](https://requests-cache.readthedocs.io/en/stable/index.html).

When you cal `/stats/` the calculation is only from local DB.

### Thinks to enhance

- [ ] More robust fetching of data (I think there is few errors)
- [ ] More tests
- [ ] Cron fetching of data

---

## Notes

### GH API

The easiest way to start interacting with the GitHub API is by using the `gh` GitHub CLI utility. You can log in, obtain an access token, and test API endpoints directly from your terminal.

For more extensive testing and exploration of the API, [RestFox](https://restfox.dev/) is a useful GUI client that simplifies making and inspecting HTTP requests.

### Pagination in GitHub API Responses

Be aware that the GitHub API often paginates its responses. When a response is paginated, the `header['link']` will contain information about the different pages. The content of the `header['link']` typically looks something like this:

```text
<https://api.github.com/repositories/1300192/issues?page=2>; rel="prev", <https://api.github.com/repositories/1300192/issues?page=4>; rel="next", <https://api.github.com/repositories/1300192/issues?page=515>; rel="last", <https://api.github.com/repositories/1300192/issues?page=1>; rel="first"
```

### Datetime

Naive datetime vs proper datetime. SQLite can store as timestamp, but
SQLAlchemy want datetime field which is without timestamp.

Assuming that all data is in UTC.
