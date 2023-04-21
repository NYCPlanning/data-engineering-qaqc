# Data Engineering Quality Control and Assurance Application

This web application displays charts and tables to assess the consistency, quality and completeness of a particular build of one of data engineering's data products.

The deployed app is at https://edm-data-engineering.nycplanningdigital.com/?page=Home

It's written in Python using the [streamlit](https://streamlit.io/) framework.

The code to produce data this application assess can be found at https://github.com/NYCPlanning/

## Dev

Best practice to run the app locally is to use the dev container (especially via VS Code)

1. From a dev container terminal, run `./entrypoint.sh`

2. If in VS Code, a popup should appear with an option to navigate to the site in a browser

3. If an error of `Access to localhost was denied` appears in the browser, try navigating to `127.0.0.1:5000` rather than `localhost:5000`

If running GRU qaqc, or working at all on github api functionality, you'll need a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). The app assumes its stored in the env variable `GHP_TOKEN`.