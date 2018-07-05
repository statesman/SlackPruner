# _domain is your slack domain. If you're chatting on mythingy.slack.com, set this to mythingy.

# daystoretain is how many days you want to keep files around. 0 purges everything, and that's bad. Perhaps you want 30 days?

# apikeys gets a list of tuples. First item in the tuple is a quoted name string, like "Mike".
# second item in the tuple is that person's API token. Get the token here: https://api.slack.com/custom-integrations/legacy-tokens
# separate the tuples with commas. Don't have a comma at the end.

# Next, a note on security. It's bad to be storing a bunch of other people's API keys. It's bad. You shouldn't do it. Security implications are obvious.
# You may not also be immediately able to use someone else's token, perhaps unless you make them an administrator and then downgrade them. That's really bad, too.

setup = {

"domain": "mythingy",

"daystoretain": 30,

"apikeys":  [
("Albert", "xoxp-1234567890-1234567890-1234567890-1234567890"),
("Betty", "xoxp-1234567890-1234567890-1234567890-1234567890"),
("Carol", "xoxp-1234567890-1234567890-1234567890-1234567890"),
("Dwayne", "xoxp-1234567890-1234567890-1234567890-1234567890")

    ]


    }
