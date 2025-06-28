I focused my time on adding one major feature and making it work. The feature I chose was web search via an external API. 
There are a few reasons I chose to go with an external API rather than the OpenAI tool:
- Much cheaper
- Better control of the web search itself (can get images etc. in the future and less limited context window). This also allows for easier debugging as we can see exactly what the search query is and the raw results.
- Compatible with a range of LLMs, not reliant on OpenAI models

For this I used the BraveSearch API and I will provide Ollie with an API key for this. 

Some of the components of getting this feature working:
- automated the decision of whether or not to search the web based on the query content and relevance of existing documents
- changed the SourceReference class to let it contain info about web sources
- adapted the SQL database schema for web sources (to track sources in the same way it was already tracking document sources)
- computed text similarity scores using the existing vector DB
- changed the sources table so that it only shows the top 4 most relevant sources to avoid clutter
- made the web source titles in the source table clickable

There's much more I would have done if I had more time! Please let me know if any of my changes are unclear or if anything doesn't work.
