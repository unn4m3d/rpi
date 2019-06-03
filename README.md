# rpi

:warning: This is very experimental

:warning: Works with development version of PlatformIO only (tested with `v4.0.0a16`)

Crystal plugin for use with [platformio](https://platformio.org). Allows writing code in Crystal targeting RaspberryPi (by default).

## Installation

1. Add the dependency to your `shard.yml`:

   ```yaml
   dependencies:
     rpi:
       github: unn4m3d/rpi
   ```

2. Run `shards install`

## Usage

Example platformio.ini configuration:

:warning: **(Linux)** You **MUST** use `https://github.com/unn4m3d/platform-linux_arm#develop` as a platform in order to compile your C/C++ code because PlatformIO doesn't provide an `arm-unknown-linux-gnueabihf` toolchain for linux x86_64

```ini

[platformio]
env_default = rpi2

[env]
extra_scripts = pre:lib/rpi/platformio_script.py
crystal_target = main # Target should be specified in shard.yml
crystal_build_flags = -Dfoo
crystal_arch = arm-unknown-linux-gnueabihf # default
crystal_shards_bin = shards # default

[env:rpi2]
platform = https://github.com/unn4m3d/platform-linux_arm#develop
board = raspberrypi_2b
```

## Todo

- [ ] Write tests
- [ ] Add support for native target (`platform - native`)
- [ ] Add support for unit testing

## Contributing

1. Fork it (<https://github.com/unn4m3d/rpi/fork>)
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request

## Contributors

- [unn4m3d](https://github.com/unn4m3d) - creator and maintainer
