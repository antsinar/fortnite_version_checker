# Fortnite Version Checker (PC only)

<!-- Badges Here -->

<!-- Project Description Here -->
> View open issues in the tags directory  

<!-- Project changelog append here -->
## 14-04-24 Barebones Version 
- Works with Fortnite installations
- Works with a single source of truth (Reddit)
- Has no dependencies, only core python libraries
- Requires Python >= 3.11.0 

### Resolved
\-

### Quality of Life issues and changes
- User has to alter the file to provide the root of the games folder (DEFAULT_GAME_ROOT is used)
  - Add command line attribute for ease of use `[QoL_0001]`
- Works with a single game
  - Add a `settings.json` file to configure runtime parameters `[QoL_0002]`
- If the source of truth detects no versions, the labels list will be empty
  - save last fetched version on every run for future reference `[QoL_0003]`
  - log behaviour and let the user know this happened `[QoL_0004]`
- Terminal use only, not as easy to use for anyone, but easily embedable
  - Create a GUI version with Beeware using current engine `[QoL_0005]`
- Using web scraping is both a memory heavy operation and quite fragile, but it was the most reliable I found
  - Serve a web api with scraped versions from as many sources as possible `[QoL_0006]`
- Works only for PC installations and releases
  - Add support for separate console releases `[QoL_0007]`

### Code Quality issues and changes
- Contains a lot of blocking behaviour inside async blocks, making the code slower. This is because the barebones version was supposed to be dependency free
  - Create an installable version with compatible async libraries to replace blocking builtins `[CQ_0001]`
- Coupling inside the main loop, instantiates a Reddit Parser class instead of using something more abstract for more control in the future
  - Use Protocols as function arguments `[CQ_0002]`  

### Bugs
- urllib.request fetches only the top 3 articles `[BUG_0001]`
- if list of post labels inside the Reddit Parser is empty (not posts found with this tag) it will raise an out-of-bounds related exception `[BUG_0002]`
<!-- EOF -->
