# s3_save_sync
Python tool for synchronising game saves to an S3 Bucket

## Configuring the bucket
Add the following environment variables to allow access to your bucket:
- `S3_SAVE_SYNC_BUCKET` = The name of your bucket.
- `S3_SAVE_SYNC_ENDPOINT` = The endpoint URL of your S3 service.
- `S3_SAVE_SYNC_KEY` = Your application key for accessing the bucket.
- `S3_SAVE_SYNC_KEY_ID` = ID for your application key for accessing the bucket.

## Configuring game saves
Configurations for game saves are configured in a toml file. This should be placed in your
user directory at `~/.s3_save_sync/game_config.toml`

The format of this file is as follows:
```toml
[RogueTrader]
name = "Rogue Trader"
[RogueTrader.Windows]
path_type = "locallow"
path = "Owlcat Games\\Warhammer 40000 Rogue Trader\\Saved Games"
```

Currently there are the following restrictions:
- Only windows is supported. May add Linux and or Mac later
- For windows, the following relative path types are supported:
    - `locallow`
    - `appdata`
    - `localappdata`
    - `userprofile`

The name field does not currently do anything but make the logs more readable. If it
is omitted the section name will be used instead. If no `path type` is specified, then
it will be assumed that the path is absolute.

Custom game settings will override default game settings of the same name.

### Games with default configurations
- Rogue Trader


## Contributing
Contributions are welcome! Please open an issue or a pull request if you have any ideas
or if you would like to contribute to the default game config list.

