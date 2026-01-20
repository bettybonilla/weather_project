### Action items

- [x] Get FastAPI “/” route working -> returns text == "hello world"
    - [x] Commit the above
- [x] In the routers folder create a new file representing a new API route
    - [x] Decide on API route request method
        - Ex: POST or GET (zip code as body or as a query param)
- [x] Add new route to FastAPI
    - [x] Test new route return “hello from “this” route”
- [x] Abstract external services in this new route
    - How should my new route interact with all 3 weather APIs?
        - Route should import a single class/function and interact with it to send the zip code and the received normalized/aggregated object back to the user
          - [x] Convert all 3 weather APIs to a type of protocol
          - [x] Review and decide what should be private
          - [x] Aggregate all weather data results in a single function to be used in this new route
- [ ] Refactor this route to be concurrent and add timeouts
  - [ ] Use a global requests.Session (dependency injection)
- [ ] Add unit tests for each weather API now that they are a type of protocol
  - [ ] Delete temp tests above the with open() statements in open_meteo, nws, weatherapi
